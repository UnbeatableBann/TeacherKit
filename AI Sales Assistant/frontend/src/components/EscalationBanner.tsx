import { AlertTriangle, UserCheck } from 'lucide-react';

export default function EscalationBanner({ reason }: { reason: string | null }) {
  return (
    <div className="bg-rose-50 border-b border-rose-200 p-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shrink-0">
      <div className="flex items-start gap-2 text-rose-900">
        <AlertTriangle className="w-5 h-5 shrink-0 text-rose-600 mt-0.5" />
        <div>
          <div className="font-semibold text-sm">Escalation Triggered</div>
          <div className="text-xs text-rose-700">{reason || "Customer needs human assistance."}</div>
        </div>
      </div>
      <div className="flex gap-2 w-full sm:w-auto">
        <button className="flex-1 sm:flex-none items-center justify-center gap-1.5 px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white text-xs font-medium rounded shadow-sm transition-colors">
          <UserCheck className="w-3.5 h-3.5" />
          Assign to Me
        </button>
        <button className="flex-1 sm:flex-none px-3 py-1.5 bg-white border border-rose-200 hover:bg-rose-50 text-rose-700 text-xs font-medium rounded shadow-sm transition-colors">
          Resolve
        </button>
      </div>
    </div>
  );
}
