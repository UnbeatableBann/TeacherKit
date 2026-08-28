import type { RequirementSchema } from '../types';

export default function RequirementsPanel({ requirements }: { requirements?: RequirementSchema }) {
  if (!requirements) return <div className="text-sm text-slate-500">No requirements extracted yet.</div>;

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 space-y-4">
      <div>
        <span className="text-xs text-slate-500 block mb-1">Category</span>
        <span className="text-sm font-medium">{requirements.category || <span className="text-slate-400 italic">Not identified</span>}</span>
      </div>
      
      <div>
        <span className="text-xs text-slate-500 block mb-1">Budget</span>
        <span className="text-sm font-medium">
          {(requirements.budget_min === null && requirements.budget_max === null) 
            ? <span className="text-slate-400 italic">Not identified</span> 
            : `${requirements.budget_min ? `$${requirements.budget_min}` : 'Any'} - ${requirements.budget_max ? `$${requirements.budget_max}` : 'Any'}`}
        </span>
      </div>
      
      <div>
        <span className="text-xs text-slate-500 block mb-2">Features Wanted</span>
        {requirements.features_wanted?.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {requirements.features_wanted.map((feat, i) => (
              <span key={i} className="px-2 py-1 bg-[var(--color-primary)]/10 text-[var(--color-primary-hover)] text-xs rounded-md">
                {feat}
              </span>
            ))}
          </div>
        ) : <span className="text-sm text-slate-400 italic">Not identified</span>}
      </div>
      
      <div>
        <span className="text-xs text-slate-500 block mb-2">Preferences</span>
        {requirements.preferences?.length > 0 ? (
          <ul className="text-sm space-y-1">
            {requirements.preferences.map((pref, i) => (
              <li key={i} className="flex items-center gap-2">
                <span className="w-1 h-1 bg-slate-400 rounded-full"></span>
                {pref}
              </li>
            ))}
          </ul>
        ) : <span className="text-sm text-slate-400 italic">Not identified</span>}
      </div>
      
      <div>
        <span className="text-xs text-slate-500 block mb-1">Urgency</span>
        <span className="text-sm font-medium">
          {requirements.urgency ? (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800">
              {requirements.urgency}
            </span>
          ) : <span className="text-slate-400 italic text-sm font-normal">Not identified</span>}
        </span>
      </div>
    </div>
  );
}


