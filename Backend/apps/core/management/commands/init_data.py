from django.core.management.base import BaseCommand
from apps.memberships.models import MembershipTier
from apps.legal.models import LegalDocument


class Command(BaseCommand):
    help = 'Initialize the database with default data'

    def handle(self, *args, **options):
        self.stdout.write('Initializing database with default data...')
        
        # Create default membership tiers
        self.create_membership_tiers()
        
        # Create default legal documents
        self.create_legal_documents()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully initialized database with default data')
        )

    def create_membership_tiers(self):
        """Create default membership tiers."""
        tiers_data = [
            {
                'name': 'trial',
                'display_name': '7-Day Trial',
                'description': 'Free trial with limited generations',
                'monthly_price': 0.00,
                'generation_limit': 10,
                'stripe_price_id': '',
                'is_active': True,
                'display_order': 0,
                'features': [
                    '10 generations',
                    'Word Downloads',
                ]
            },
            {
                'name': 'starter',
                'display_name': 'Starter',
                'description': 'Perfect for teachers getting started with AI-generated content',
                'monthly_price': 12.00,
                'generation_limit': 40,
                'stripe_price_id': '',
                'is_active': True,
                'display_order': 1,
                'features': [
                    '40 generations',
                    'Word Downloads',
                    'Save & Manage Content in Dashboard',
                ]
            },
            {
                'name': 'pro',
                'display_name': 'Pro',
                'description': 'For professional educators who need unlimited content generation',
                'monthly_price': 25.00,
                'generation_limit': None,  # Unlimited
                'stripe_price_id': '',
                'is_active': True,
                'display_order': 2,
                'features': [
                    'Unlimited generations',
                    'Word Downloads',
                    'Save & Manage Content in Dashboard',
                    'Priority Support',
                    'Early Access to New Tools',
                ]
            }
        ]
        
        for tier_data in tiers_data:
            tier, created = MembershipTier.objects.get_or_create(
                name=tier_data['name'],
                defaults=tier_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created membership tier: {tier.display_name}')
                )
            else:
                self.stdout.write(
                    f'Membership tier already exists: {tier.display_name}'
                )

    def create_legal_documents(self):
        """Create default legal documents."""
        legal_docs_data = [
            {
                'document_type': 'terms_of_service',
                'title': 'Terms of Service',
                'content': '''Please replace this with your actual Terms of Service.

These terms govern your use of our services. By accessing or using our platform, you agree to these terms and our Privacy Policy.

1. **Acceptance of Terms**
   By using our services, you acknowledge that you have read, understood, and agree to be bound by these terms.

2. **Changes to Terms**
   We reserve the right to modify these terms at any time. We will notify you of any changes by posting the new terms on our website.

3. **Use of Services**
   You agree to use our services only for lawful purposes and in accordance with these terms.

4. **Intellectual Property**
   All content and materials provided through our services are owned by us or our licensors.

5. **Disclaimer of Warranties**
   Our services are provided "as is" without any warranties of any kind.

6. **Limitation of Liability**
   We shall not be liable for any indirect, incidental, special, consequential or punitive damages.

7. **Governing Law**
   These terms shall be governed by the laws of your jurisdiction.''',
                'version': '1.0',
                'is_active': True
            },
            {
                'document_type': 'privacy_policy',
                'title': 'Privacy Policy',
                'content': '''Please replace this with your actual Privacy Policy.

This Privacy Policy describes how we collect, use, and share your personal information when you use our services.

1. **Information We Collect**
   - Account information (name, email address)
   - Usage data (how you interact with our services)
   - Device information (IP address, browser type)

2. **How We Use Your Information**
   - To provide and improve our services
   - To communicate with you
   - To comply with legal obligations

3. **Sharing Your Information**
   We do not sell or rent your personal information to third parties.

4. **Data Security**
   We implement reasonable security measures to protect your information.

5. **Your Rights**
   You have the right to access, update, or delete your personal information.

6. **Cookies**
   We use cookies to enhance your experience on our platform.

7. **Changes to This Policy**
   We may update this policy from time to time. We will notify you of any changes.

8. **Contact Us**
   If you have any questions about this Privacy Policy, please contact us.''',
                'version': '1.0',
                'is_active': True
            }
        ]
        
        for doc_data in legal_docs_data:
            doc, created = LegalDocument.objects.get_or_create(
                document_type=doc_data['document_type'],
                defaults=doc_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created legal document: {doc.title}')
                )
            else:
                self.stdout.write(
                    f'Legal document already exists: {doc.title}'
                )