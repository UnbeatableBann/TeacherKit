import type { RecommendationSchema } from '../types';
import { CheckCircle2 } from 'lucide-react';

export default function RecommendationCard({ recommendation }: { recommendation: RecommendationSchema }) {
  return (
    <div className="bg-white border border-indigo-100 rounded-lg p-4 shadow-sm relative overflow-hidden group hover:border-indigo-300 transition-colors">
      <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500"></div>
      
      <div className="flex justify-between items-start mb-2">
        <h4 className="font-semibold text-slate-900 leading-tight">{recommendation.name}</h4>
        <span className="font-bold text-indigo-700 whitespace-nowrap ml-2">${recommendation.price}</span>
      </div>
      
      <p className="text-sm text-slate-600 mb-3">{recommendation.reasoning}</p>
      
      {recommendation.matched_features?.length > 0 && (
        <div className="space-y-1">
          <div className="text-xs font-semibold text-slate-500">Matched Features</div>
          {recommendation.matched_features.map((f, i) => (
            <div key={i} className="flex items-start gap-1.5 text-xs text-slate-700">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 mt-0.5 shrink-0" />
              <span>{f}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
