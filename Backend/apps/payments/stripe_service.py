import stripe
from django.conf import settings
from django.utils import timezone
from .models import StripeCustomer, PaymentHistory
from apps.accounts.models import User
from apps.memberships.models import UserMembership

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """
    Service to handle Stripe integration for payments and subscriptions.
    """

    @staticmethod
    def get_or_create_customer(user):
        """
        Get or create a Stripe customer for a user.
        """
        try:
            stripe_customer = user.stripe_customer
            # Update customer details if needed
            stripe.Customer.modify(
                stripe_customer.stripe_customer_id,
                email=user.email,
                name=f"{user.first_name} {user.last_name}"
            )
            return stripe_customer.stripe_customer_id
        except StripeCustomer.DoesNotExist:
            # Create a new Stripe customer
            customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}",
                metadata={'user_id': user.id}
            )
            
            # Save to our database
            stripe_customer = StripeCustomer.objects.create(
                user=user,
                stripe_customer_id=customer.id
            )
            return customer.id

    @staticmethod
    def create_checkout_session(user, price_id, success_url, cancel_url):
        """
        Create a Stripe checkout session for a subscription.
        """
        customer_id = StripeService.get_or_create_customer(user)
        
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'user_id': user.id,
            }
        )
        return checkout_session

    @staticmethod
    def create_payment_intent(user, amount, currency='usd', description=''):
        """
        Create a Stripe payment intent for one-time payments.
        """
        customer_id = StripeService.get_or_create_customer(user)
        
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency=currency,
            customer=customer_id,
            description=description,
            metadata={
                'user_id': user.id,
            }
        )
        
        # Save to our database
        payment_history = PaymentHistory.objects.create(
            user=user,
            stripe_payment_intent_id=payment_intent.id,
            amount=amount,
            currency=currency,
            description=description
        )
        
        return payment_intent

    @staticmethod
    def handle_subscription_updated(subscription):
        """
        Handle Stripe subscription.updated webhook event.
        """
        try:
            customer_id = subscription['customer']
            stripe_customer = StripeCustomer.objects.get(stripe_customer_id=customer_id)
            user = stripe_customer.user
            
            # Get or create user membership
            membership, created = UserMembership.objects.get_or_create(user=user)
            
            # Update membership details
            membership.stripe_subscription_id = subscription['id']
            membership.status = subscription['status']
            
            from datetime import datetime
            if subscription['current_period_start']:
                membership.current_period_start = datetime.fromtimestamp(
                    subscription['current_period_start'], tz=timezone.utc
                ).date()
            
            if subscription['current_period_end']:
                membership.current_period_end = datetime.fromtimestamp(
                    subscription['current_period_end'], tz=timezone.utc
                ).date()
            
            # Update tier based on price (simplified - in reality you'd map prices to tiers)
            if subscription['items']['data']:
                price_id = subscription['items']['data'][0]['price']['id']
                # Find tier by stripe_price_id
                from apps.memberships.models import MembershipTier
                try:
                    tier = MembershipTier.objects.get(stripe_price_id=price_id)
                    membership.tier = tier
                except MembershipTier.DoesNotExist:
                    pass  # Handle appropriately in real implementation
            
            membership.save()
            
            return True
        except StripeCustomer.DoesNotExist:
            return False

    @staticmethod
    def handle_invoice_paid(invoice):
        """
        Handle Stripe invoice.paid webhook event.
        """
        try:
            customer_id = invoice['customer']
            stripe_customer = StripeCustomer.objects.get(stripe_customer_id=customer_id)
            user = stripe_customer.user
            
            # Create payment history record
            PaymentHistory.objects.create(
                user=user,
                stripe_payment_intent_id=invoice['payment_intent'],
                amount=invoice['amount_paid'] / 100,  # Convert from cents
                currency=invoice['currency'],
                status='succeeded',
                description=f"Invoice {invoice['id']}",
                metadata={
                    'invoice_id': invoice['id'],
                    'hosted_invoice_url': invoice['hosted_invoice_url'],
                }
            )
            
            return True
        except StripeCustomer.DoesNotExist:
            return False

    @staticmethod
    def handle_invoice_payment_failed(invoice):
        """
        Handle Stripe invoice.payment_failed webhook event.
        """
        try:
            customer_id = invoice['customer']
            stripe_customer = StripeCustomer.objects.get(stripe_customer_id=customer_id)
            user = stripe_customer.user
            
            # Create payment history record
            PaymentHistory.objects.create(
                user=user,
                stripe_payment_intent_id=invoice['payment_intent'],
                amount=invoice['amount_due'] / 100,  # Convert from cents
                currency=invoice['currency'],
                status='failed',
                description=f"Failed invoice {invoice['id']}",
                metadata={
                    'invoice_id': invoice['id'],
                }
            )
            
            return True
        except StripeCustomer.DoesNotExist:
            return False

    @staticmethod
    def create_customer_portal_session(user, return_url):
        """
        Create a Stripe customer portal session for managing subscription and payment methods.
        """
        try:
            customer_id = StripeService.get_or_create_customer(user)
            
            portal_session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return portal_session
        except StripeCustomer.DoesNotExist:
            raise ValueError("Stripe customer not found for user")