import type { NextBestActionSchema } from '../types';
import { Lightbulb } from 'lucide-react';

export default function NextBestActionCard({ action }: { action: NextBestActionSchema }) {
  return (
    <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 shadow-sm">
      <div className="flex items-center gap-2 mb-1.5">
        <Lightbulb className="w-4 h-4 text-amber-600" />
        <h4 className="text-xs font-bold text-amber-900 uppercase tracking-wider">Next Best Action</h4>
      </div>
      <div className="font-medium text-amber-950 text-sm mb-1 capitalize">
        {action.action.replace(/_/g, ' ')}
      </div>
      <p className="text-xs text-amber-800/80">
        {action.reason}
      </p>
    </div>
  );
}
