"""
Management command to load legal documents from client specifications.

Usage:
    python manage.py load_legal_documents
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.legal.models import LegalDocument
from datetime import datetime


class Command(BaseCommand):
    help = 'Load legal documents (Terms of Service, Privacy Policy, Acceptable Use Policy)'

    def _format_section_headings(self, content):
        """Add bold formatting to section headings."""
        lines = content.split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Skip empty lines and already formatted lines
            if not stripped or '<strong>' in line:
                formatted_lines.append(line)
                continue
            
            # Check if this looks like a heading:
            # - Not too long (less than 60 chars)
            # - Doesn't end with punctuation (except colon)
            # - Next line is either empty or starts content
            # - Not part of a list
            is_heading = (
                len(stripped) < 60 and 
                not stripped.startswith('-') and
                not stripped.startswith('•') and
                not stripped[0].isdigit() and
                not stripped.endswith('.') and
                not stripped.endswith(',') and
                stripped[0].isupper() and
                (i == 0 or i == len(lines) - 1 or lines[i + 1].strip() == '' or not lines[i + 1].strip()[0].isupper() or len(lines[i + 1].strip()) > 60)
            )
            
            if is_heading and stripped not in ['Terms of Service', 'Acceptable Use Policy', 'Privacy Policy']:
                formatted_lines.append(f'<strong>{stripped}</strong>')
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)

    def handle(self, *args, **options):
        self.stdout.write('Loading legal documents...')
        
        # Get current date in readable format
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Terms of Service
        terms_content = f"""Thank you for using this platform. These Terms of Service explain the rules you agree to when you create an account, use the generators, or download materials from this site. By signing up or using the platform in any way, you agree to follow these terms.

If you do not agree with these terms, please do not use the platform.

<strong>Overview of the Service</strong>
This platform provides AI powered tools that help teachers create educational materials. Users can generate lesson resources, download them, and use them in their classrooms or personal teaching work. The platform is not a marketplace and does not sell user generated files.

<strong>Eligibility</strong>
To use the platform, you must:
Be at least 18 years old
Create an account with accurate information
Agree to these Terms of Service
Follow all laws in your area while using the service

If you create an account for an organization, you confirm that you have permission to do so.

<strong>Your Account</strong>
You are responsible for keeping your account and password safe. If you believe someone else is using your account, you must tell us right away. We may suspend or close accounts that break these terms or pose a security risk.

<strong>Paid Plans and Billing</strong>
The platform offers different membership levels.
The Starter plan includes limited generations each month.
The Pro plan includes unlimited generations.

<strong>You agree that:</strong>
Payments are processed on a recurring basis until you cancel
You will not share your account with others
Refunds are not guaranteed and are handled case by case
All prices may change. If prices change, you will be notified before the new price begins.

<strong>AI Generated Content</strong>
The platform uses artificial intelligence to help create text and documents. You are responsible for reviewing and editing anything you generate. You understand that:
AI outputs may contain errors
AI outputs may need correction before classroom use
You are responsible for how you use the materials you create
We do not guarantee that all outputs will be accurate, complete, or fit your exact needs.

<strong>Ownership of Content</strong>
You own the materials you create using the generators. You may use them in your classroom, personal teaching business, or for other lawful educational purposes.

You agree not to claim that the platform or its creators produced the final work. You also agree not to use AI generated content in a way that violates copyright laws or harms others.

The platform owns its software, designs, tools, generators, and website content. You may not copy, sell, or reverse engineer the platform or its features.

<strong>Acceptable Use</strong>
You agree not to use the platform to:
Break any laws
Generate harmful or inappropriate content
Harass or harm others
Misuse the software or overload the system
Try to access areas you are not allowed to access
Try to copy the code, design, or structure of the platform

We may suspend or remove accounts that break these rules.

<strong>Service Changes</strong>
We may update or change the platform at any time. We may add new features, remove features, or fix technical issues. Although we try to avoid interruptions, the service may go offline for maintenance or repairs.

<strong>Disclaimer</strong>
The platform is provided as is. We do not promise that the service will always be available, error free, or meet every user's needs. You use the platform at your own risk.

<strong>Limitation of Liability</strong>
To the fullest extent allowed by law:
We are not responsible for losses caused by system errors, downtime, or incorrect AI outputs
We are not responsible for business losses, student outcomes, or damages from misused content
Our total liability will never be more than the amount you paid for the service during the last thirty days

<strong>Cancellation and Termination</strong>
You may cancel your subscription at any time from your account page. You will continue to have access until the end of your billing period.

We may suspend or end your account if you:
Break these terms
Abuse the system
Cause security or legal problems

<strong>Changes to These Terms</strong>
We may update these Terms of Service from time to time. When changes are made, the new version will be posted on the site. Continued use of the service means you accept the updated terms.

<strong>Contact Information</strong>
If you have questions about these terms, you may contact us at: admin@foodsciencetoolbox.com"""

        # Acceptable Use Policy
        aup_content = f"""<strong>Introduction</strong>
This Acceptable Use Policy explains the rules you must follow when using this platform. These rules protect the safety, integrity, and experience of all users. By creating an account or using the service, you agree to follow this policy.

<strong>General Responsibilities</strong>
You must use the platform in a lawful, respectful, and responsible way. You are responsible for your account activity, the content you generate, and any materials you upload or download.

<strong>Prohibited Activities</strong>
You may not use the platform to break laws, harm others, or disrupt the system. Prohibited activities include harassment, hate speech, threats, generating harmful or abusive content, distributing viruses or malware, attempting to access accounts that are not yours, reverse engineering the platform, or using automated tools to overload or misuse the system.

<strong>AI Usage Rules</strong>
You agree not to use AI-generated content to spread misinformation, produce harmful materials, or break school, district, or legal guidelines. You are responsible for reviewing and correcting AI-generated materials before using them with students or the public.

<strong>Security Requirements</strong>
You may not attempt to bypass security features, share your password, or allow unauthorized users to access your account. If you notice suspicious activity, you must notify us immediately.

<strong>Respect for Intellectual Property</strong>
You must not upload or generate content that violates copyrights, trademarks, or the intellectual property rights of others. You may only upload or use materials you have permission to use.

<strong>Misuse of the Service</strong>
You may not copy, sell, or redistribute the platform's software, design, layout, or internal tools. You may not use the service to build a competing product or attempt to extract or replicate its code, structure, or features.

<strong>Protection of Minors</strong>
You may not use the platform to create harmful, explicit, or inappropriate content involving minors. This is strictly banned and may result in immediate account removal and legal action.

<strong>Consequences for Violations</strong>
We may suspend or permanently remove your account if you break this policy. Severe violations may also lead to legal action. No refunds will be issued if an account is terminated for misconduct.

<strong>Reporting Problems</strong>
If you experience a safety issue, see misuse, or have concerns about content, you should contact us right away so the issue can be reviewed and addressed.

<strong>Changes to This Policy</strong>
We may update this Acceptable Use Policy at any time. When changes are made, the updated version will be posted on the website. Continued use of the service means you accept the updated rules.

<strong>Contact Information</strong>
For questions or concerns about this policy, contact us at: admin@foodsciencetoolbox.com."""

        # Privacy Policy (basic version - needs to be expanded)
        privacy_content = f"""<strong>Introduction</strong>
This Privacy Policy explains how we collect, use, and protect your personal information when you use this platform.

<strong>Information We Collect</strong>
We collect information you provide when creating an account, including your name, email address, and payment information. We also collect usage data about how you interact with the platform.

<strong>How We Use Your Information</strong>
We use your information to provide and improve our services, process payments, communicate with you, and ensure platform security.

<strong>Data Security</strong>
We implement appropriate security measures to protect your personal information. However, no method of transmission over the internet is 100% secure.

<strong>Your Rights</strong>
You have the right to access, update, or delete your personal information. You can do this through your account settings or by contacting us.

<strong>Contact Information</strong>
For questions about this privacy policy, contact us at: admin@foodsciencetoolbox.com."""

        documents = [
            {
                'document_type': 'terms_of_service',
                'title': 'Terms of Service',
                'content': terms_content,
                'version': '1.0'
            },
            {
                'document_type': 'acceptable_use',
                'title': 'Acceptable Use Policy',
                'content': aup_content,
                'version': '1.0'
            },
            {
                'document_type': 'privacy_policy',
                'title': 'Privacy Policy',
                'content': privacy_content,
                'version': '1.0'
            }
        ]

        for doc_data in documents:
            # Format section headings as bold
            formatted_content = self._format_section_headings(doc_data['content'])
            
            doc, created = LegalDocument.objects.update_or_create(
                document_type=doc_data['document_type'],
                defaults={
                    'title': doc_data['title'],
                    'content': formatted_content,
                    'version': doc_data['version'],
                    'is_active': True,
                    'published_at': timezone.now()
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created {doc_data["title"]}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Updated {doc_data["title"]}')
                )

        self.stdout.write(self.style.SUCCESS('Legal documents loaded successfully!'))

