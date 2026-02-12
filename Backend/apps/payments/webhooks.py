import stripe
import logging
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from apps.memberships.models import UserMembership
from apps.payments.models import PaymentHistory, StripeCustomer
from apps.notifications.tasks import send_upgrade_confirmation_email

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    """
    Handle Stripe webhook events.
    This endpoint is CSRF exempt because Stripe uses its own signature verification.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return HttpResponse(status=400)
    
    # Handle different event types
    handlers = {
        'checkout.session.completed': handle_checkout_session_completed,
        'invoice.payment_succeeded': handle_payment_succeeded,
        'invoice.payment_failed': handle_payment_failed,
        'customer.subscription.updated': handle_subscription_updated,
        'customer.subscription.deleted': handle_subscription_deleted,
    }
    
    handler = handlers.get(event['type'])
    if handler:
        try:
            handler(event['data']['object'])
        except Exception as e:
            logger.error(f"Error handling {event['type']}: {e}")
            return HttpResponse(status=500)
    
    return HttpResponse(status=200)


@transaction.atomic
def handle_checkout_session_completed(session):
    """Handle successful checkout session completion"""
    try:
        user_id = session.get('metadata', {}).get('user_id')
        if not user_id:
            logger.warning("No user_id in checkout session metadata")
            return
        
        from apps.accounts.models import User
        user = User.objects.get(id=user_id)
        
        # Get subscription from session
        subscription_id = session.get('subscription')
        if subscription_id:
            subscription = stripe.Subscription.retrieve(subscription_id)
            handle_subscription_updated(subscription)
        
        logger.info(f"Checkout session completed for user: {user.email}")
    except Exception as e:
        logger.error(f"Error handling checkout session completed: {e}")


@transaction.atomic
def handle_payment_succeeded(invoice):
    """Handle successful payment"""
    try:
        subscription_id = invoice.get('subscription')
        customer_id = invoice.get('customer')
        amount_paid = invoice.get('amount_paid', 0) / 100  # Convert cents to dollars
        
        if not subscription_id:
            logger.warning("No subscription ID in invoice")
            return
        
        # Retrieve subscription to get billing interval
        subscription = stripe.Subscription.retrieve(subscription_id)
        handle_subscription_updated(subscription)
        
        # Find membership
        try:
            membership = UserMembership.objects.get(stripe_subscription_id=subscription_id)
        except UserMembership.DoesNotExist:
            logger.warning(f"Membership not found for subscription: {subscription_id}")
            return
        
        # Log payment
        PaymentHistory.objects.create(
            user=membership.user,
            stripe_payment_intent_id=invoice.get('payment_intent', ''),
            amount=amount_paid,
            currency=invoice.get('currency', 'usd'),
            status='succeeded',
            description=f"Invoice {invoice.get('id', '')}",
            metadata={
                'invoice_id': invoice.get('id'),
                'hosted_invoice_url': invoice.get('hosted_invoice_url'),
            }
        )
        
        # Update membership status
        membership.status = 'active'
        if invoice.get('period_end'):
            membership.current_period_end = datetime.fromtimestamp(
                invoice.get('period_end'), tz=timezone.utc
            ).date()
        membership.save(update_fields=['status', 'current_period_end', 'updated_at'])
        
        logger.info(f"Payment succeeded for user: {membership.user.email}")
    
    except Exception as e:
        logger.error(f"Error handling payment succeeded: {e}")


@transaction.atomic
def handle_payment_failed(invoice):
    """Handle failed payment"""
    try:
        subscription_id = invoice.get('subscription')
        
        if not subscription_id:
            return
        
        membership = UserMembership.objects.get(stripe_subscription_id=subscription_id)
        membership.status = 'past_due'
        membership.save(update_fields=['status', 'updated_at'])
        
        # Log failed payment
        PaymentHistory.objects.create(
            user=membership.user,
            stripe_payment_intent_id=invoice.get('payment_intent', ''),
            amount=invoice.get('amount_due', 0) / 100,
            currency=invoice.get('currency', 'usd'),
            status='failed',
            description=f"Failed invoice {invoice.get('id', '')}",
            metadata={
                'invoice_id': invoice.get('id'),
            }
        )
        
        logger.warning(f"Payment failed for user: {membership.user.email}")
    
    except UserMembership.DoesNotExist:
        logger.warning(f"Membership not found for subscription: {subscription_id}")
    except Exception as e:
        logger.error(f"Error handling payment failed: {e}")


@transaction.atomic
def handle_subscription_updated(subscription):
    """Handle subscription update"""
    try:
        subscription_id = subscription.get('id')
        customer_id = subscription.get('customer')
        
        if not subscription_id:
            return
        
        # Find Stripe customer
        try:
            stripe_customer = StripeCustomer.objects.get(stripe_customer_id=customer_id)
        except StripeCustomer.DoesNotExist:
            logger.warning(f"Stripe customer not found: {customer_id}")
            return
        
        user = stripe_customer.user
        
        # Get or create membership
        membership, created = UserMembership.objects.get_or_create(
            user=user,
            defaults={'tier_id': 1}  # Default to first tier, should be updated
        )
        
        # Update membership details
        membership.stripe_subscription_id = subscription_id
        membership.status = subscription.get('status', 'active')
        membership.stripe_customer_id = customer_id
        
        if subscription.get('current_period_start'):
            membership.current_period_start = datetime.fromtimestamp(
                subscription.get('current_period_start'), tz=timezone.utc
            ).date()
        
        if subscription.get('current_period_end'):
            membership.current_period_end = datetime.fromtimestamp(
                subscription.get('current_period_end'), tz=timezone.utc
            ).date()
        
        # Update tier based on price and extract billing interval
        if subscription.get('items', {}).get('data'):
            price_data = subscription['items']['data'][0]['price']
            price_id = price_data['id']
            
            # Extract billing interval from Stripe price
            if price_data.get('recurring'):
                interval = price_data['recurring'].get('interval', 'month')
                membership.billing_interval = 'year' if interval == 'year' else 'month'
            
            from apps.memberships.models import MembershipTier
            try:
                tier = MembershipTier.objects.get(stripe_price_id=price_id)
                membership.tier = tier
                # If user has a paid subscription (not trial), ensure status is active
                if tier.name != 'trial' and membership.status == 'trialing':
                    membership.status = 'active'
            except MembershipTier.DoesNotExist:
                logger.warning(f"Tier not found for price_id: {price_id}")
        
        # Calculate billing interval from period dates if not set
        if not membership.billing_interval and membership.current_period_start and membership.current_period_end:
            from datetime import timedelta
            period_days = (membership.current_period_end - membership.current_period_start).days
            # If period is around 365 days, it's yearly; otherwise monthly
            if period_days >= 300:  # Yearly (allowing some variance)
                membership.billing_interval = 'year'
            elif period_days >= 25:  # Monthly (allowing some variance)
                membership.billing_interval = 'month'
        
        membership.save()
        
        # Send upgrade confirmation if this is a new subscription
        if created or subscription.get('status') == 'active':
            send_upgrade_confirmation_email.delay(
                user.email,
                membership.tier.display_name
            )
        
        logger.info(f"Subscription updated for user: {user.email}")
    
    except Exception as e:
        logger.error(f"Error handling subscription updated: {e}")


@transaction.atomic
def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    try:
        subscription_id = subscription.get('id')
        
        if not subscription_id:
            return
        
        membership = UserMembership.objects.get(stripe_subscription_id=subscription_id)
        membership.status = 'canceled'
        membership.save(update_fields=['status', 'updated_at'])
        
        logger.info(f"Subscription canceled for user: {membership.user.email}")
    
    except UserMembership.DoesNotExist:
        logger.warning(f"Membership not found for subscription: {subscription_id}")
    except Exception as e:
        logger.error(f"Error handling subscription deleted: {e}")

