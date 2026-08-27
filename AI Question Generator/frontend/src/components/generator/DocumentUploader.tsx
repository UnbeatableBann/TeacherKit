import { useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, Loader2, XCircle } from 'lucide-react';
import { DocumentResponse } from '@/types';

interface DocumentUploaderProps {
  documents: DocumentResponse[];
  onFileSelect: (file: File) => void;
  onRemove: (documentId: string) => void;
}

export function DocumentUploader({ documents, onFileSelect, onRemove }: DocumentUploaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      Array.from(e.target.files).forEach(file => {
        onFileSelect(file);
      });
      // reset input so the same file can be selected again if needed
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'uploading':
      case 'processing':
      case 'uploaded':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <FileText className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusText = (status: string, progress?: number) => {
    switch (status) {
      case 'ready': return 'Ready';
      case 'failed': return 'Failed';
      case 'processing': return 'Processing...';
      case 'uploaded': return 'Processing...';
      case 'uploading': return `Uploading... ${progress || 0}%`;
      default: return status;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-foreground">Previous-year papers</h3>
        
        <div>
          <input
            type="file"
            accept="application/pdf"
            multiple
            className="hidden"
            ref={fileInputRef}
            onChange={handleFileChange}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="inline-flex items-center gap-2 text-sm text-primary hover:text-primary-hover font-medium"
            type="button"
          >
            <UploadCloud className="w-4 h-4" />
            + Add PDF
          </button>
        </div>
      </div>
      
      {documents.length > 0 ? (
        <div className="space-y-2">
          {documents.map((doc) => (
            <div key={doc.document_id} className="relative overflow-hidden p-3 bg-card border border-border rounded-lg shadow-sm animate-in fade-in flex items-center justify-between">
              
              {doc.status === 'uploading' && (
                <div 
                  className="absolute bottom-0 left-0 h-1 bg-blue-500 transition-all duration-300"
                  style={{ width: `${doc.uploadProgress || 0}%` }}
                />
              )}

              <div className="flex items-center gap-3 overflow-hidden">
                <FileText className="w-5 h-5 text-indigo-500 shrink-0" />
                <span className="text-sm font-medium truncate" title={doc.filename}>{doc.filename}</span>
              </div>
              <div className="flex items-center gap-4 shrink-0 pl-4">
                <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                  {getStatusIcon(doc.status)}
                  <span className={doc.status === 'failed' ? 'text-red-500' : ''}>
                    {getStatusText(doc.status, doc.uploadProgress)}
                  </span>
                </div>
                <button 
                  onClick={() => onRemove(doc.document_id)}
                  className="text-muted-foreground hover:text-destructive transition-colors text-xs"
                  title="Remove document"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="border border-dashed border-border rounded-lg bg-card/50 p-6 flex flex-col items-center justify-center text-center text-muted-foreground">
          <UploadCloud className="w-8 h-8 mb-2 opacity-50" />
          <p className="text-sm font-medium">No documents uploaded</p>
          <p className="text-xs mt-1">Upload PDF examination papers to begin</p>
        </div>
      )}
    </div>
  );
}
