import type { KnowledgeDocument } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function transformDocument(doc: any): KnowledgeDocument {
  // Convert byte size to MB string and created_at to upload_date for frontend compatibility
  const sizeMB = doc.size ? (doc.size / (1024 * 1024)).toFixed(2) + ' MB' : undefined;
  
  // Title case status from backend (processing -> Processing)
  const statusFormatted = doc.status 
    ? doc.status.charAt(0).toUpperCase() + doc.status.slice(1) 
    : 'Unknown';
    
  return {
    id: doc.id,
    filename: doc.filename,
    status: statusFormatted as any,
    upload_date: doc.created_at,
    size: sizeMB
  };
}

export async function fetchDocuments(): Promise<KnowledgeDocument[]> {
  const res = await fetch(`${API_BASE}/knowledge-base/documents?tenant_id=default_tenant`);
  if (!res.ok) throw new Error('Failed to fetch documents');
  const data = await res.json();
  return (data.documents || []).map(transformDocument);
}

export async function uploadDocument(file: File, tenantId: string = 'default_tenant'): Promise<KnowledgeDocument> {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await fetch(`${API_BASE}/knowledge-base/documents?tenant_id=${tenantId}`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to upload document');
  const data = await res.json();
  
  // The upload returns {document_id, status}. We need to fetch the full document to return it,
  // or return a placeholder that will be updated by polling.
  return {
    id: data.document_id,
    filename: file.name,
    status: data.status.charAt(0).toUpperCase() + data.status.slice(1) as any,
    upload_date: new Date().toISOString(),
    size: `${(file.size / (1024 * 1024)).toFixed(2)} MB`
  };
}

export async function removeDocument(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/knowledge-base/documents/${id}?tenant_id=default_tenant`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete document');
}

export async function checkDocumentStatus(id: string): Promise<KnowledgeDocument | null> {
  const res = await fetch(`${API_BASE}/knowledge-base/documents/${id}?tenant_id=default_tenant`);
  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error('Failed to fetch document status');
  }
  const data = await res.json();
  return transformDocument(data);
}
