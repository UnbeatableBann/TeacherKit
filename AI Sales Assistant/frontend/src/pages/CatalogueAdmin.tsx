import { useState } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle } from 'lucide-react';


const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function CatalogueAdmin() {
  const [file, setFile] = useState<File | null>(null);
  const [tenantId, setTenantId] = useState('default_tenant');
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setStatus('idle');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const res = await fetch(`${API_URL}/catalogue/upload?tenant_id=${tenantId}`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Upload failed');
      setStatus('success');
      setFile(null);
    } catch (err) {
      console.error(err);
      setStatus('error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-3xl mx-auto space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Catalogue Management</h1>
          <p className="text-slate-500 mt-1">Upload and manage product catalogues for tenants.</p>
        </div>
        
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Upload CSV Catalogue</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Tenant ID</label>
              <input
                type="text"
                value={tenantId}
                onChange={e => setTenantId(e.target.value)}
                className="w-full max-w-sm px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            
            <div className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer relative">
              <input 
                type="file" 
                accept=".csv" 
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                onChange={e => e.target.files && setFile(e.target.files[0])}
              />
              <div className="flex flex-col items-center justify-center gap-2 pointer-events-none">
                <FileText className="w-8 h-8 text-slate-400" />
                {file ? (
                  <span className="font-medium text-slate-700">{file.name}</span>
                ) : (
                  <span className="text-slate-500">Drop a CSV file here, or click to select</span>
                )}
              </div>
            </div>
            
            <div className="flex items-center gap-4 pt-2">
              <button
                onClick={handleUpload}
                disabled={!file || uploading}
                className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white font-medium rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors"
              >
                <Upload className="w-4 h-4" />
                {uploading ? 'Uploading & Indexing...' : 'Upload & Index'}
              </button>
              
              {status === 'success' && (
                <div className="flex items-center gap-2 text-emerald-600 font-medium text-sm">
                  <CheckCircle2 className="w-4 h-4" />
                  Catalogue ingested and indexing started in background.
                </div>
              )}
              {status === 'error' && (
                <div className="flex items-center gap-2 text-rose-600 font-medium text-sm">
                  <AlertCircle className="w-4 h-4" />
                  Upload failed. Please try again.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
