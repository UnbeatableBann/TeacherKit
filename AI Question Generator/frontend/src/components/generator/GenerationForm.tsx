
import { GenerationRequest } from '@/types';
import { Label } from '@/components/ui/label';
import { NativeSelect } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

interface GenerationFormProps {
  config: Partial<GenerationRequest>;
  onChange: (updates: Partial<GenerationRequest>) => void;
  onSubmit: () => void;
  isGenerating: boolean;
  canGenerate: boolean;
  validationError?: string;
}

export function GenerationForm({ 
  config, 
  onChange, 
  onSubmit, 
  isGenerating, 
  canGenerate,
  validationError
}: GenerationFormProps) {
  
  return (
    <div className="card-container p-6 space-y-6">
      <h3 className="font-semibold text-lg border-b border-border pb-3">Generation Configuration</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <Label>Subject</Label>
          <NativeSelect 
            value={config.subject || ""} 
            onChange={(e) => onChange({ subject: e.target.value })}
            className="w-full bg-white"
          >
            <option value="" disabled>Select subject</option>
            <option value="Mathematics">Mathematics</option>
            <option value="Science">Science</option>
            <option value="English">English</option>
            <option value="General">General</option>
          </NativeSelect>
        </div>

        <div className="space-y-2">
          <Label>Class / Level</Label>
          <NativeSelect 
            value={config.class_level || ""} 
            onChange={(e) => onChange({ class_level: e.target.value })}
            className="w-full bg-white"
          >
            <option value="" disabled>Select class</option>
            <option value="Standard 8">Standard 8</option>
            <option value="Standard 9">Standard 9</option>
            <option value="Standard 10">Standard 10</option>
            <option value="Standard 11">Standard 11</option>
            <option value="Standard 12">Standard 12</option>
            <option value="Undergraduate">Undergraduate</option>
          </NativeSelect>
        </div>

        <div className="space-y-2">
          <Label>Topic</Label>
          <Input 
            className="w-full bg-white"
            placeholder="e.g., Algebra, Physics" 
            value={config.requested_topic || ""}
            onChange={(e) => onChange({ requested_topic: e.target.value })}
          />
        </div>

        <div className="space-y-2">
          <Label>Number of Questions</Label>
          <Input 
            type="number" 
            className="w-full bg-white"
            placeholder="20" 
            min={1}
            max={50}
            value={config.total_questions || ""}
            onChange={(e) => onChange({ total_questions: parseInt(e.target.value) || 0 })}
          />
        </div>

        <div className="space-y-2">
          <Label>Difficulty</Label>
          <NativeSelect 
            value={config.requested_difficulty || ""} 
            onChange={(e) => onChange({ requested_difficulty: e.target.value as any })}
            className="w-full bg-white"
          >
            <option value="" disabled>Select difficulty</option>
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard</option>
          </NativeSelect>
        </div>
      </div>

      <div className="pt-4 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="text-sm text-error font-medium h-5">
          {validationError}
        </div>
        <Button 
          className="w-full sm:w-auto min-w-[200px]"
          onClick={onSubmit} 
          disabled={!canGenerate || isGenerating}
        >
          {isGenerating ? "Generating questions..." : "Generate Questions"}
        </Button>
      </div>
    </div>
  );
}
