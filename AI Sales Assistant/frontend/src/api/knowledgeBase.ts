import type { KnowledgeDocument } from '../types';
import { mockDocuments } from '../mock/knowledgeBase';

// Fake delay
const delay = (ms: number) => new Promise(res => setTimeout(res, ms));

// Keep local state for the mock
let documents = [...mockDocuments];

export async function fetchDocuments(): Promise<KnowledgeDocument[]> {
  await delay(500);
  return [...documents];
}

export async function uploadDocument(file: File, _tenantId: string): Promise<KnowledgeDocument> {
  await delay(800);
  const newDoc: KnowledgeDocument = {
    id: `doc-${Date.now()}`,
    filename: file.name,
    status: 'Processing',
    upload_date: new Date().toISOString(),
    size: `${(file.size / (1024 * 1024)).toFixed(2)} MB`
  };
  documents = [newDoc, ...documents];
  
  // Simulate processing finishing after a bit
  setTimeout(() => {
    const idx = documents.findIndex(d => d.id === newDoc.id);
    if (idx !== -1) {
      documents[idx].status = 'Ready';
    }
  }, 4000);
  
  return newDoc;
}

export async function removeDocument(id: string): Promise<void> {
  await delay(800);
  documents = documents.filter(doc => doc.id !== id);
}

export async function checkDocumentStatus(id: string): Promise<KnowledgeDocument | null> {
  await delay(200);
  const doc = documents.find(d => d.id === id);
  return doc || null;
}
