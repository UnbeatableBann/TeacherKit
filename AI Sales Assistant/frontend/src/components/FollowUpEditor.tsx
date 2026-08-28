import { useState, useEffect } from 'react';
import { useGenerateFollowUp } from '../api/hooks';
import { X, Send } from 'lucide-react';

export default function FollowUpEditor({ conversationId, onClose }: { conversationId: string; onClose: () => void }) {
  const { mutateAsync: generate, isPending } = useGenerateFollowUp();
  const [draft, setDraft] = useState('');
  
  useEffect(() => {
    generate(conversationId).then(res => setDraft(res.draft_text)).catch(console.error);
  }, [conversationId, generate]);

  return (
    <div className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 bg-slate-50">
          <h2 className="font-semibold text-slate-800">Draft Follow-up</h2>
          <button onClick={onClose} className="p-1 hover:bg-slate-200 rounded-md text-slate-500 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-4 flex-1">
          {isPending && !draft ? (
            <div className="flex items-center justify-center h-40 text-slate-400 text-sm">
              Generating draft grounded in confirmed state...
            </div>
          ) : (
            <textarea
              className="w-full h-64 p-3 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] resize-none text-sm"
              value={draft}
              onChange={e => setDraft(e.target.value)}
              placeholder="Email draft..."
            />
          )}
        </div>
        
        <div className="px-4 py-3 border-t border-slate-100 bg-slate-50 flex justify-end gap-2">
          <button 
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 transition-colors"
          >
            Cancel
          </button>
          <button 
            disabled={isPending || !draft}
            className="flex items-center gap-2 px-4 py-2 bg-[var(--color-primary)] text-white text-sm font-medium rounded-md hover:bg-[var(--color-primary-hover)] disabled:opacity-50 transition-colors"
          >
            <Send className="w-4 h-4" />
            Send Follow-up
          </button>
        </div>
      </div>
    </div>
  );
}


