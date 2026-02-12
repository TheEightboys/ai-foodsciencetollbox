from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import LegalDocument


class LegalDocumentModelTest(TestCase):
    def setUp(self):
        # Create legal document
        self.terms_of_service = LegalDocument.objects.create(
            document_type='terms_of_service',
            title='Terms of Service',
            content='These are the terms of service.',
            version='1.0',
            is_active=True
        )

    def test_legal_document_creation(self):
        self.assertEqual(self.terms_of_service.document_type, 'terms_of_service')
        self.assertEqual(self.terms_of_service.title, 'Terms of Service')
        self.assertEqual(self.terms_of_service.content, 'These are the terms of service.')
        self.assertEqual(self.terms_of_service.version, '1.0')
        self.assertTrue(self.terms_of_service.is_active)

    def test_legal_document_string_representation(self):
        expected_str = 'Terms of Service (v1.0)'
        self.assertEqual(str(self.terms_of_service), expected_str)


class LegalDocumentAPITest(TestCase):
    def setUp(self):
        # Create legal document
        self.terms_of_service = LegalDocument.objects.create(
            document_type='terms_of_service',
            title='Terms of Service',
            content='These are the terms of service.',
            version='1.0',
            is_active=True
        )
        
        # Create API client
        self.client = APIClient()

    def test_legal_document_list(self):
        # Make request
        response = self.client.get(reverse('legal:document-list'))
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['document_type'], 'terms_of_service')
        self.assertEqual(response.data[0]['title'], 'Terms of Service')
        
    def test_legal_document_detail(self):
        # Make request
        response = self.client.get(reverse('legal:document-detail', kwargs={'pk': self.terms_of_service.pk}))
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['document_type'], 'terms_of_service')
        self.assertEqual(response.data['title'], 'Terms of Service')
        self.assertEqual(response.data['content'], 'These are the terms of service.')
        
    def test_legal_document_by_type(self):
        # Make request
        response = self.client.get(reverse('legal:document-by-type', kwargs={'document_type': 'terms_of_service'}))
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['document_type'], 'terms_of_service')
        self.assertEqual(response.data['title'], 'Terms of Service')
        
    def test_legal_document_inactive_not_listed(self):
        # Create inactive document
        LegalDocument.objects.create(
            document_type='privacy_policy',
            title='Privacy Policy',
            content='This is the privacy policy.',
            version='1.0',
            is_active=False
        )
        
        # Make request
        response = self.client.get(reverse('legal:document-list'))
        
        # Check response - should only return active documents
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['document_type'], 'terms_of_service')