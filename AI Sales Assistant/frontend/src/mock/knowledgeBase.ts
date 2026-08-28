import type { KnowledgeDocument } from '../types';

export const mockDocuments: KnowledgeDocument[] = [
  {
    id: 'doc-1',
    filename: 'product_catalogue.pdf',
    status: 'Ready',
    upload_date: new Date(Date.now() - 86400000 * 2).toISOString(),
    size: '2.4 MB'
  },
  {
    id: 'doc-2',
    filename: 'pricing.pdf',
    status: 'Ready',
    upload_date: new Date(Date.now() - 86400000 * 1).toISOString(),
    size: '1.1 MB'
  },
  {
    id: 'doc-3',
    filename: 'enterprise_services.pdf',
    status: 'Processing',
    upload_date: new Date().toISOString(),
    size: '5.7 MB'
  }
];
