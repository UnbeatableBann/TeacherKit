import type { RequirementSchema } from '../types';

export default function RequirementsPanel({ requirements }: { requirements?: RequirementSchema }) {
  if (!requirements) return <div className="text-sm text-slate-500">No requirements extracted yet.</div>;

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 space-y-4">
      {requirements.category && (
        <div>
          <span className="text-xs text-slate-500 block mb-1">Category</span>
          <span className="text-sm font-medium">{requirements.category}</span>
        </div>
      )}
      
      {(requirements.budget_min !== null || requirements.budget_max !== null) && (
        <div>
          <span className="text-xs text-slate-500 block mb-1">Budget</span>
          <span className="text-sm font-medium">
            {requirements.budget_min ? `$${requirements.budget_min}` : 'Any'} - {requirements.budget_max ? `$${requirements.budget_max}` : 'Any'}
          </span>
        </div>
      )}
      
      {requirements.features_wanted?.length > 0 && (
        <div>
          <span className="text-xs text-slate-500 block mb-2">Features Wanted</span>
          <div className="flex flex-wrap gap-2">
            {requirements.features_wanted.map((feat, i) => (
              <span key={i} className="px-2 py-1 bg-indigo-50 text-indigo-700 text-xs rounded-md">
                {feat}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {requirements.preferences?.length > 0 && (
        <div>
          <span className="text-xs text-slate-500 block mb-2">Preferences</span>
          <ul className="text-sm space-y-1">
            {requirements.preferences.map((pref, i) => (
              <li key={i} className="flex items-center gap-2">
                <span className="w-1 h-1 bg-slate-400 rounded-full"></span>
                {pref}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {requirements.urgency && (
        <div>
          <span className="text-xs text-slate-500 block mb-1">Urgency</span>
          <span className="text-sm inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800">
            {requirements.urgency}
          </span>
        </div>
      )}
    </div>
  );
}
