import { useState, useEffect, useRef } from 'react';
import { Upload, FileText, AlertCircle, Trash2, Loader2, X } from 'lucide-react';
import { fetchDocuments, uploadDocument, removeDocument, checkDocumentStatus } from '../api/knowledgeBase';
import type { KnowledgeDocument } from '../types';
import { cn } from '../lib/utils';

export default function CatalogueAdmin() {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [tenantId] = useState('default_tenant');
  const [error, setError] = useState<string | null>(null);
  
  // Confirmation state
  const [documentToRemove, setDocumentToRemove] = useState<KnowledgeDocument | null>(null);
  const [isRemoving, setIsRemoving] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load documents
  const loadDocs = async () => {
    try {
      const docs = await fetchDocuments();
      setDocuments(docs);
    } catch (err) {
      setError('Failed to load knowledge base documents.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  // Poll processing documents
  useEffect(() => {
    const processingDocs = documents.filter(d => d.status === 'Processing' || d.status === 'Uploading');
    if (processingDocs.length === 0) return;

    const interval = setInterval(async () => {
      let changed = false;
      const updatedDocs = await Promise.all(documents.map(async doc => {
        if ((doc.status === 'Processing' || doc.status === 'Uploading') && !doc.id.startsWith('temp-')) {
          const updated = await checkDocumentStatus(doc.id);
          if (updated && updated.status !== doc.status) {
            changed = true;
            return updated;
          }
        }
        return doc;
      }));

      if (changed) {
        setDocuments(updatedDocs);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [documents]);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    e.target.value = ''; // Reset input
    
    try {
      // Optimistically add uploading state
      const tempDoc: KnowledgeDocument = {
        id: `temp-${Date.now()}`,
        filename: file.name,
        status: 'Uploading',
      };
      setDocuments(prev => [tempDoc, ...prev]);
      
      const newDoc = await uploadDocument(file, tenantId);
      
      // Replace temp with actual
      setDocuments(prev => prev.map(d => d.id === tempDoc.id ? newDoc : d));
    } catch (err) {
      setError('Failed to upload document.');
      loadDocs(); // reload to clear temp state
    }
  };

  const confirmRemove = async () => {
    if (!documentToRemove) return;
    setIsRemoving(true);
    try {
      // set Removing status visually
      setDocuments(prev => prev.map(d => d.id === documentToRemove.id ? { ...d, status: 'Removing' } : d));
      await removeDocument(documentToRemove.id);
      setDocuments(prev => prev.filter(d => d.id !== documentToRemove.id));
    } catch (err) {
      setError('Failed to remove document.');
      loadDocs();
    } finally {
      setIsRemoving(false);
      setDocumentToRemove(null);
    }
  };

  return (
    <div className="h-full w-full overflow-y-auto bg-slate-50 p-6 lg:p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Knowledge Base</h1>
          <p className="text-slate-500 mt-1">Upload product or service documents</p>
        </div>
        
        {error && (
          <div className="bg-rose-50 border border-rose-200 text-rose-700 px-4 py-3 rounded-md flex items-start justify-between">
            <div className="flex gap-2 items-center">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <p className="text-sm font-medium">{error}</p>
            </div>
            <button onClick={() => setError(null)} className="text-rose-500 hover:text-rose-700">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Upload Section */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <div className="space-y-4">
            <div className="flex items-center gap-4 border-2 border-dashed border-slate-300 rounded-lg p-8 bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer relative"
                 onClick={() => fileInputRef.current?.click()}
            >
              <input 
                type="file" 
                ref={fileInputRef}
                accept=".pdf,.csv,.txt,.docx" 
                className="hidden"
                onChange={handleFileChange}
              />
              <div className="flex-1 flex flex-col items-center justify-center gap-2 pointer-events-none">
                <Upload className="w-8 h-8 text-[var(--color-primary)] opacity-80" />
                <span className="font-medium text-slate-700">Select documents</span>
                <span className="text-slate-500 text-sm">or drag and drop</span>
              </div>
            </div>
          </div>
        </div>

        {/* Document List */}
        <div>
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Current Knowledge Base Documents</h2>
          
          {isLoading ? (
            <div className="flex justify-center p-8 text-slate-500">
              <Loader2 className="w-6 h-6 animate-spin" />
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center p-12 bg-white rounded-xl border border-slate-200 shadow-sm">
              <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
              <h3 className="text-slate-900 font-medium mb-1">No documents yet.</h3>
              <p className="text-slate-500 text-sm max-w-sm mx-auto mb-4">
                Upload your product or service catalogue to enable grounded recommendations.
              </p>
              <button 
                onClick={() => fileInputRef.current?.click()}
                className="px-4 py-2 bg-[var(--color-primary)] text-white rounded-md hover:bg-[var(--color-primary-hover)] text-sm font-medium transition-colors"
              >
                Upload document
              </button>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <ul className="divide-y divide-slate-100">
                {documents.map(doc => (
                  <li key={doc.id} className="flex items-center justify-between p-4 hover:bg-slate-50/50 transition-colors">
                    <div className="flex items-start gap-3">
                      <FileText className={cn("w-5 h-5 shrink-0 mt-0.5", 
                        doc.status === 'Ready' ? 'text-[var(--color-primary)]' : 'text-slate-400'
                      )} />
                      <div>
                        <p className="font-medium text-slate-900 text-sm">{doc.filename}</p>
                        <div className="flex items-center gap-3 mt-1 text-xs text-slate-500">
                          <span className={cn(
                            "flex items-center gap-1 font-medium",
                            doc.status === 'Ready' && "text-emerald-600",
                            (doc.status === 'Processing' || doc.status === 'Uploading') && "text-amber-600",
                            doc.status === 'Failed' && "text-rose-600",
                          )}>
                            {(doc.status === 'Processing' || doc.status === 'Uploading' || doc.status === 'Removing') && (
                              <Loader2 className="w-3 h-3 animate-spin" />
                            )}
                            {doc.status}
                          </span>
                          {doc.size && <span>• {doc.size}</span>}
                          {doc.upload_date && <span>• {new Date(doc.upload_date).toLocaleDateString()}</span>}
                        </div>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => setDocumentToRemove(doc)}
                      disabled={doc.status === 'Removing'}
                      className="text-slate-400 hover:text-rose-600 p-2 rounded-md hover:bg-rose-50 transition-colors disabled:opacity-50"
                      aria-label="Remove document"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Remove Confirmation Dialog */}
      {documentToRemove && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Remove document?</h3>
            <p className="text-slate-600 text-sm mb-6">
              <span className="font-semibold text-slate-900">{documentToRemove.filename}</span> will no longer be available to the AI assistant.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDocumentToRemove(null)}
                disabled={isRemoving}
                className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmRemove}
                disabled={isRemoving}
                className="px-4 py-2 text-sm font-medium text-white bg-rose-600 rounded-md hover:bg-rose-700 transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {isRemoving ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                {isRemoving ? 'Removing...' : 'Remove'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


