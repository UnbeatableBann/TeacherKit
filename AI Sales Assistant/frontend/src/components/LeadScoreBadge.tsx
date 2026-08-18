import type { LeadScoreSchema } from '../types';

export default function LeadScoreBadge({ score }: { score?: LeadScoreSchema }) {
  if (!score) return null;

  return (
    <div className="flex items-center gap-3 bg-white px-3 py-2 border border-slate-200 rounded-lg shadow-sm">
      <div className="text-center">
        <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Score</div>
        <div className={`text-2xl font-bold ${score.score >= 70 ? 'text-emerald-600' : 'text-slate-700'}`}>
          {score.score}
        </div>
      </div>
      <div className="border-l border-slate-100 pl-3 flex-1">
        <div className="text-[10px] text-slate-500 mb-1 font-medium">BREAKDOWN</div>
        <div className="space-y-0.5">
          {Object.entries(score.breakdown || {}).map(([key, val]) => (
            <div key={key} className="flex justify-between text-xs">
              <span className="text-slate-600 capitalize">{key.replace('_', ' ')}</span>
              <span className="font-medium">+{val as React.ReactNode}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
