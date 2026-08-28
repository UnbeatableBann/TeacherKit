import { Outlet, Link, useParams } from 'react-router-dom';
import { useLeads } from '../api/hooks';
import { Users, AlertTriangle } from 'lucide-react';
import { cn } from '../lib/utils';

export default function Dashboard() {
  const { data: leads, isLoading } = useLeads();
  const { id: activeId } = useParams();

  return (
    <div className="flex h-full w-full bg-slate-50 text-slate-900">
      {/* Sidebar */}
      <div className="w-80 flex-shrink-0 border-r border-slate-200 bg-white flex flex-col">
        <div className="p-4 border-b border-slate-200 flex items-center gap-2 font-semibold">
          <Users className="w-5 h-5 text-[var(--color-primary)]" />
          Active Leads
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


