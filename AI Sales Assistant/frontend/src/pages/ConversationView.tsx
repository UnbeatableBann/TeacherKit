import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useConversation, useSendMessage } from '../api/hooks';
import ConversationThread from '../components/ConversationThread';
import RequirementsPanel from '../components/RequirementsPanel';
import LeadScoreBadge from '../components/LeadScoreBadge';
import RecommendationCard from '../components/RecommendationCard';
import NextBestActionCard from '../components/NextBestActionCard';
import EscalationBanner from '../components/EscalationBanner';
import FollowUpEditor from '../components/FollowUpEditor';
import type { OrchestratorResponse } from '../types';

export default function ConversationView() {
  const { id } = useParams<{ id: string }>();
  const { data: state, isLoading } = useConversation(id!);
  const { mutateAsync: sendMessage, isPending } = useSendMessage();
  
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);
  const [latestResponse, setLatestResponse] = useState<OrchestratorResponse | null>(null);
  const [input, setInput] = useState('');
  const [showFollowUp, setShowFollowUp] = useState(false);

  if (isLoading) return <div className="p-8">Loading...</div>;

  const handleSend = async () => {
    if (!input.trim()) return;
    const msg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: msg }]);
    
    try {
      const result = await sendMessage({ id: id!, message: msg });
      setLatestResponse(result);
      
      // If there are answered questions, append them
      if (result.answered_questions?.length) {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: result.answered_questions.map(q => `**${q.question}**\n${q.answer}`).join('\n\n') 
        }]);
      } else if (result.next_best_action?.action === "clarify_requirements") {
        setMessages(prev => [...prev, { role: 'assistant', content: "Could you tell me more about your requirements?" }]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex-1 flex h-full overflow-hidden">
      {/* Thread Area */}
      <div className="flex-1 flex flex-col border-r border-slate-200">
        {latestResponse?.escalation?.triggered && (
          <EscalationBanner reason={latestResponse.escalation.reason} />
        )}
        
        <div className="flex-1 overflow-y-auto p-4 bg-slate-50/50">
          <ConversationThread messages={messages} />
        </div>
        
        <div className="p-4 bg-white border-t border-slate-200">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              placeholder="Type a customer message to simulate..."
              className="flex-1 px-4 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              disabled={isPending}
            />
            <button
              onClick={handleSend}
              disabled={isPending}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              {isPending ? 'Sending...' : 'Send'}
            </button>
            <button
              onClick={() => setShowFollowUp(true)}
              className="px-4 py-2 border border-slate-300 text-slate-700 rounded-md hover:bg-slate-50"
            >
              Draft Follow-up
            </button>
          </div>
        </div>
      </div>
      
      {/* Context Panel */}
      <div className="w-80 lg:w-96 flex-shrink-0 bg-slate-50 overflow-y-auto border-l border-slate-200">
        <div className="p-4 space-y-6">
          {/* Lead Score & Next Action */}
          <div className="flex items-start justify-between gap-4">
            <LeadScoreBadge score={latestResponse?.lead_score || state?.lead_score} />
          </div>
          
          {latestResponse?.next_best_action && (
            <NextBestActionCard action={latestResponse.next_best_action} />
          )}

          {/* Requirements */}
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Requirements</h3>
            <RequirementsPanel requirements={latestResponse?.requirements || state?.requirements} />
          </div>

          {/* Recommendations */}
          {(((latestResponse?.recommendations?.length ?? 0) > 0) || ((state?.recommendations_shown?.length ?? 0) > 0)) && (
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Top Recommendations</h3>
              <div className="space-y-3">
                {(latestResponse?.recommendations || state?.recommendations_shown).map((rec: any) => (
                  <RecommendationCard key={rec.product_id} recommendation={rec} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {showFollowUp && (
        <FollowUpEditor conversationId={id!} onClose={() => setShowFollowUp(false)} />
      )}
    </div>
  );
}
