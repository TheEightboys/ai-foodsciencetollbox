import apiClient from './client';

export type DownloadFormat = 'word' | 'pdf';

class DownloadService {
  async downloadContent(contentId: number, format: DownloadFormat): Promise<Blob> {
    const response = await apiClient.get(`/downloads/content/${contentId}/download/`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  }

  async downloadAsFile(contentId: number, format: DownloadFormat, filename?: string): Promise<void> {
    const blob = await this.downloadContent(contentId, format);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || `content.${format === 'word' ? 'docx' : 'pdf'}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}

export const downloadService = new DownloadService();

