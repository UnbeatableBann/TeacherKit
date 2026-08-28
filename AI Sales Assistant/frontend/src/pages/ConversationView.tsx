import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useConversation, useSendMessage } from '../api/hooks';
import ConversationThread from '../components/ConversationThread';
import RequirementsPanel from '../components/RequirementsPanel';
import { Copy, Check, RefreshCw } from 'lucide-react';
import type { OrchestratorResponse } from '../types';

export default function ConversationView() {
  const { id } = useParams<{ id: string }>();
  const { isLoading } = useConversation(id!);
  const { mutateAsync: sendMessage, isPending } = useSendMessage();
  
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);
  const [latestResponse, setLatestResponse] = useState<OrchestratorResponse | null>(null);
  const [input, setInput] = useState('');
  const [copied, setCopied] = useState(false);

  if (isLoading) return <div className="p-8">Loading...</div>;

  const handleSend = async () => {
    if (!input.trim()) return;
    const msg = input;
    setInput('');
    // Treat the input as customer conversation.
    setMessages(prev => [...prev, { role: 'customer', content: msg }]);
    
    try {
      const result = await sendMessage({ id: id!, message: msg });
      setLatestResponse(result);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCopy = () => {
    if (latestResponse?.follow_up_message) {
      navigator.clipboard.writeText(latestResponse.follow_up_message);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleRegenerate = async () => {
    if (messages.length === 0) return;
    try {
      // Just re-send the last message for now to regenerate
      const msg = messages[messages.length - 1].content;
      const result = await sendMessage({ id: id!, message: msg });
      setLatestResponse(result);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex-1 flex h-full overflow-hidden">
      {/* Thread Area */}
      <div className="flex-1 flex flex-col border-r border-slate-200 bg-white">
        
        {messages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-slate-500">
            <h2 className="text-xl font-semibold text-slate-700 mb-2">Generate a customer follow-up</h2>
            <p className="max-w-md">
              Paste a customer message or conversation to get recommendations and a ready-to-send follow-up.
            </p>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto p-4 bg-[var(--color-primary)]/5">
            <ConversationThread messages={messages} />
          </div>
        )}
        
        <div className="p-4 bg-white border-t border-slate-200">
          <div className="flex flex-col gap-2">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Paste a customer message or conversation..."
              className="w-full min-h-[80px] max-h-48 px-4 py-3 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] resize-y"
              disabled={isPending}
            />
            <div className="flex justify-end">
              <button
                onClick={handleSend}
                disabled={isPending}
                className="px-6 py-2 bg-[var(--color-primary)] text-white font-medium rounded-md hover:bg-[var(--color-primary-hover)] disabled:opacity-50 transition-colors"
              >
                {isPending ? 'Generating follow-up...' : 'Send'}
              </button>
            </div>
            {isPending && (
              <div className="text-xs text-slate-500 text-right mt-1">
                Analyzing customer request...
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Context Panel */}
      <div className="w-[400px] flex-shrink-0 bg-slate-50 overflow-y-auto border-l border-slate-200">
        <div className="p-4 space-y-6">
          
          {/* Customer Analysis */}
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Customer Requirements</h3>
            {latestResponse?.requirements ? (
              <div className="space-y-4">
                <div className="bg-white p-3 rounded-md border border-slate-200 text-sm">
                  <div className="text-xs font-medium text-slate-500 uppercase mb-1">Intent</div>
                  <div className="text-slate-800">{latestResponse.intent || 'Not identified'}</div>
                </div>
                
                <RequirementsPanel requirements={latestResponse.requirements} />
                
                <div className="bg-white p-3 rounded-md border border-slate-200 text-sm">
                  <div className="text-xs font-medium text-slate-500 uppercase mb-1">Objections</div>
                  {latestResponse.objections?.length > 0 ? (
                    <ul className="list-disc pl-4 text-slate-800">
                      {latestResponse.objections.map((obj, i) => (
                        <li key={i}>{obj.text}</li>
                      ))}
                    </ul>
                  ) : (
                    <div className="text-slate-500">None identified</div>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-sm text-slate-500 italic">Submit a message to see analysis.</div>
            )}
          </div>

          {/* Recommendations */}
          {latestResponse && (
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Recommendations</h3>
              {latestResponse.recommendations?.length > 0 ? (
                <div className="space-y-3">
                  {latestResponse.recommendations.map((rec, idx) => (
                    <div key={idx} className="bg-white border border-slate-200 rounded-md p-3">
                      <div className="font-semibold text-slate-800 mb-2">{rec.name}</div>
                      <div className="text-xs font-medium text-slate-500 uppercase mb-1">Why it matches</div>
                      <p className="text-sm text-slate-600 mb-3">{rec.reasoning}</p>
                      
                      {rec.sources && rec.sources.length > 0 && (
                        <div>
                          <div className="text-xs font-medium text-slate-500 uppercase mb-1">Source</div>
                          <div className="text-xs text-slate-500 bg-slate-100 p-1 rounded inline-block">
                            {rec.sources.join(', ')}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-slate-500 bg-white border border-slate-200 p-3 rounded-md">
                  None
                </div>
              )}
            </div>
          )}

          {/* Follow-up Message */}
          {latestResponse?.follow_up_message && (
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Follow-up Message</h3>
              <div className="bg-white border border-slate-200 rounded-md flex flex-col">
                <textarea
                  className="w-full h-48 p-3 text-sm text-slate-800 resize-y focus:outline-none"
                  value={latestResponse.follow_up_message}
                  onChange={(e) => setLatestResponse({...latestResponse, follow_up_message: e.target.value})}
                />
                <div className="border-t border-slate-100 p-2 flex justify-end gap-2 bg-slate-50">
                  <button
                    onClick={handleRegenerate}
                    disabled={isPending}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 bg-white border border-slate-200 rounded hover:bg-slate-50 transition-colors disabled:opacity-50"
                  >
                    <RefreshCw className="w-3 h-3" />
                    Regenerate
                  </button>
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-[var(--color-primary)] rounded hover:bg-[var(--color-primary-hover)] transition-colors"
                  >
                    {copied ? (
                      <>
                        <Check className="w-3 h-3" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        Copy
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}
          
        </div>
      </div>
    </div>
  );
}
