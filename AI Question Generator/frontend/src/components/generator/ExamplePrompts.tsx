
import { Lightbulb } from 'lucide-react';
import { GenerationRequest } from '@/types';

interface ExamplePromptsProps {
  onSelect: (config: Partial<GenerationRequest>) => void;
}

export function ExamplePrompts({ onSelect }: ExamplePromptsProps) {
  const examples = [
    {
      label: "Mathematics: Class 10 Algebra",
      description: "Generate 20 medium-difficulty Class 10 mathematics questions on algebra based on the uploaded papers.",
      config: {
        subject: "Mathematics",
        class_level: "Standard 10",
        requested_topic: "Algebra",
        total_questions: 20,
        requested_difficulty: "Medium" as const
      }
    },
    {
      label: "Science: Class 8 Basics",
      description: "Create 10 easy Science questions for Class 8 focusing on recurring topics from the uploaded papers.",
      config: {
        subject: "Science",
        class_level: "Standard 8",
        requested_topic: "Recurring patterns",
        total_questions: 10,
        requested_difficulty: "Easy" as const
      }
    },
    {
      label: "Mathematics: Hard Patterns",
      description: "Generate 15 hard Mathematics questions following the difficulty and marks pattern of the uploaded papers.",
      config: {
        subject: "Mathematics",
        class_level: "Standard 12",
        requested_topic: "General",
        total_questions: 15,
        requested_difficulty: "Hard" as const
      }
    }
  ];

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-sm font-medium text-foreground">
        <Lightbulb className="w-4 h-4 text-amber-500" />
        Try an example
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {examples.map((ex, idx) => (
          <button
            key={idx}
            onClick={() => onSelect(ex.config)}
            className="text-left p-4 bg-card hover:bg-slate-50 border border-border rounded-lg transition-colors group flex flex-col gap-2 shadow-sm"
          >
            <div className="text-sm font-semibold text-foreground group-hover:text-primary transition-colors">
              {ex.label}
            </div>
            <div className="text-xs text-muted-foreground leading-relaxed line-clamp-3">
              "{ex.description}"
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
