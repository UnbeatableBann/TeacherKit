import { Outlet, Link, useParams, useNavigate } from 'react-router-dom';
import { useLeads, useCreateConversation } from '../api/hooks';
import { Users, AlertTriangle, Plus, X } from 'lucide-react';
import { cn } from '../lib/utils';
import { useState } from 'react';

export default function Dashboard() {
  const { data: leads, isLoading } = useLeads();
  const { id: activeId } = useParams();
  const navigate = useNavigate();
  const { mutateAsync: createConversation, isPending } = useCreateConversation();
  
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newCustomerName, setNewCustomerName] = useState("");

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCustomerName.trim()) return;
    try {
      const res = await createConversation({ customer_name: newCustomerName.trim() });
      setShowCreateModal(false);
      setNewCustomerName("");
      navigate(`/conversations/${res.conversation_id}`);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex h-full w-full bg-slate-50 text-slate-900 relative">
      {showCreateModal && (
        <div className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 bg-slate-50">
              <h2 className="font-semibold text-slate-800">New Conversation</h2>
              <button onClick={() => setShowCreateModal(false)} className="p-1 hover:bg-slate-200 rounded-md text-slate-500 transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreate} className="p-4">
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-1">Customer Name</label>
                <input
                  type="text"
                  value={newCustomerName}
                  onChange={(e) => setNewCustomerName(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                  placeholder="e.g. Acme Corp"
                  autoFocus
                />
              </div>
              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-md transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isPending || !newCustomerName.trim()}
                  className="px-4 py-2 bg-[var(--color-primary)] text-white text-sm font-medium rounded-md hover:bg-[var(--color-primary-hover)] disabled:opacity-50 transition-colors"
                >
                  {isPending ? "Creating..." : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Sidebar */}
      <div className="w-80 flex-shrink-0 border-r border-slate-200 bg-white flex flex-col">
        <div className="p-4 border-b border-slate-200 flex items-center justify-between font-semibold">
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-[var(--color-primary)]" />
            Active Leads
          </div>
          <button 
            onClick={() => setShowCreateModal(true)}
            className="p-1 hover:bg-slate-100 rounded-md transition-colors text-slate-600 hover:text-[var(--color-primary)] disabled:opacity-50"
            title="New Conversation"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 text-sm text-slate-500">Loading leads...</div>
          ) : (
            <div className="flex flex-col">
              {leads?.map((lead) => (
                <Link
                  key={lead.conversation_id}
                  to={`/conversations/${lead.conversation_id}`}
                  className={cn(
                    "p-4 border-b border-slate-100 hover:bg-slate-50 flex items-start justify-between cursor-pointer transition-colors",
                    activeId === lead.conversation_id && "bg-[var(--color-primary)]/10 border-l-2 border-l-[var(--color-primary)]"
                  )}
                >
                  <div className="flex flex-col">
                    <span className="font-medium">{lead.customer_name}</span>
                    <span className="text-xs text-slate-500 mt-1">
                      {new Date(lead.last_activity).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    {/* Using escalation flag from backend if present */}
                    {lead.escalation_triggered && <AlertTriangle className="w-4 h-4 text-amber-500" />}
                    <span className={cn(
                      "text-xs px-2 py-1 rounded-full font-medium",
                      lead.score >= 70 ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-700"
                    )}>
                      {lead.score}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex min-w-0 bg-white">
        {activeId ? (
          <Outlet />
        ) : (
          <div className="flex-1 flex items-center justify-center text-slate-400">
            Select a lead to view conversation
          </div>
        )}
      </div>
    </div>
  );
}


