/**
 * Legal Document Page Component
 * 
 * Displays legal documents (Terms of Service, Privacy Policy, Acceptable Use Policy)
 * fetched from the backend API.
 */

import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { AxiosError } from 'axios';

interface LegalDocument {
  document_type: string;
  title: string;
  content: string;
  version: string;
  published_at: string;
}

const DOCUMENT_TYPE_MAP: Record<string, string> = {
  'terms-of-service': 'terms_of_service',
  'terms': 'terms_of_service',
  'privacy-policy': 'privacy_policy',
  'privacy': 'privacy_policy',
  'acceptable-use': 'acceptable_use',
  'acceptable-use-policy': 'acceptable_use',
};

export default function LegalDocumentPage() {
  const { documentType } = useParams<{ documentType: string }>();
  const [document, setDocument] = useState<LegalDocument | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchDocument = async () => {
      // Handle direct routes like /terms, /privacy, /acceptable-use
      let docType = documentType;
      if (!docType) {
        const path = window.location.pathname;
        if (path === '/terms') docType = 'terms';
        else if (path === '/privacy') docType = 'privacy';
        else if (path === '/acceptable-use') docType = 'acceptable-use';
      }
      
      if (!docType) {
        setError('Invalid document type');
        setLoading(false);
        return;
      }

      try {
        const apiType = DOCUMENT_TYPE_MAP[docType] || docType;
        const { default: apiClient } = await import('@/lib/api/client');
        const response = await apiClient.get(`/legal/documents/type/${apiType}/`);
        
        if (response.data) {
          setDocument(response.data);
        } else {
          setError('Document not found');
        }
      } catch (err) {
        const axiosError = err as AxiosError<{ detail?: string; message?: string }>;
        
        if (axiosError.response?.status === 404) {
          setError('Document not found. Please ensure legal documents are loaded in the database (run `python manage.py load_legal_documents`).');
        } else if (!axiosError.response) {
          setError('Unable to connect to server. Please check your connection and try again.');
        } else {
          setError(axiosError.response?.data?.detail 
            || axiosError.response?.data?.message 
            || axiosError.message 
            || 'Failed to load document');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDocument();
  }, [documentType]);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </DashboardLayout>
    );
  }

  if (error || !document) {
    return (
      <DashboardLayout>
        <Card>
          <CardHeader>
            <CardTitle>Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-destructive">{error || 'Document not found'}</p>
          </CardContent>
        </Card>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">{document.title}</CardTitle>
            <p className="text-sm text-muted-foreground">
              Version {document.version} • Last Updated: {new Date(document.published_at).toLocaleDateString()}
            </p>
          </CardHeader>
          <CardContent>
            <div 
              className="prose prose-sm max-w-none dark:prose-invert legal-document"
              style={{ whiteSpace: 'pre-wrap' }}
              dangerouslySetInnerHTML={{ 
                __html: document.content
                  // Convert markdown headers to bold HTML if not already formatted
                  .replace(/^(#{1,6})\s+(.+)$/gm, (match, hashes, text) => {
                    return `<p><strong>${text}</strong></p>`;
                  })
                  // Convert **text** to bold
                  .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                  // Preserve line breaks
                  .replace(/\n/g, '<br>')
              }}
            />
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

