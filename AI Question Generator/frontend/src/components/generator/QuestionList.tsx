import { useState } from 'react';
import { GeneratedQuestionResponse, GenerationResponse } from '@/types';
import { ChevronDown, ChevronUp, CheckCircle, AlertTriangle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface QuestionListProps {
  response: GenerationResponse;
}

export function QuestionList({ response }: QuestionListProps) {
  if (!response.questions || response.questions.length === 0) {
    return (
      <div className="card-container p-8 text-center text-muted-foreground flex flex-col items-center">
        <AlertTriangle className="w-8 h-8 mb-3 text-amber-500" />
        <p className="font-medium text-foreground">No valid questions generated</p>
        <p className="text-sm mt-1">Try adjusting your topic or difficulty constraints.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* Summary Header */}
      <div className="card-container p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-100 flex flex-col sm:flex-row justify-between items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Generated {response.generated_count} Questions</h2>
          <div className="text-sm text-slate-600 mt-1 flex items-center gap-2 flex-wrap">
            <span>{response.subject}</span>
            <span>•</span>
            <span>{response.class_level}</span>
            {response.questions[0]?.topic && (
              <>
                <span>•</span>
                <span>{response.questions[0].topic}</span>
              </>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-full border border-blue-100 shadow-sm text-sm">
          <CheckCircle className="w-4 h-4 text-green-500" />
          <span className="font-medium text-slate-700">{response.generated_count}/{response.requested_count} Passed</span>
        </div>
      </div>

      {/* Questions */}
      <div className="space-y-4">
        {response.questions.map((q, idx) => (
          <QuestionCard key={q.id || idx} question={q} index={idx + 1} />
        ))}
      </div>
    </div>
  );
}

function QuestionCard({ question, index }: { question: GeneratedQuestionResponse; index: number }) {
  const [showAnswer, setShowAnswer] = useState(false);

  return (
    <div className="card-container overflow-hidden bg-white">
      <div className="p-5">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-4">
          <h3 className="font-semibold text-lg text-foreground">Question {index}</h3>
          
          <div className="flex flex-wrap gap-2">
            {question.topic && <Badge variant="secondary" className="bg-slate-100 text-slate-700">{question.topic}</Badge>}
            {question.difficulty && (
              <Badge variant="outline" className={
                question.difficulty === 'Easy' ? 'border-green-200 text-green-700' :
                question.difficulty === 'Medium' ? 'border-amber-200 text-amber-700' :
                'border-red-200 text-red-700'
              }>
                {question.difficulty}
              </Badge>
            )}
            {question.marks && <Badge className="bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border-indigo-200">{question.marks} Marks</Badge>}
          </div>
        </div>

        <div className="prose prose-sm max-w-none text-slate-800 whitespace-pre-wrap">
          {question.question_text}
        </div>

        {question.answer && (
          <button
            onClick={() => setShowAnswer(!showAnswer)}
            className="mt-6 text-sm font-medium text-primary hover:text-primary-hover flex items-center gap-1 transition-colors"
          >
            {showAnswer ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            {showAnswer ? "Hide Answer & Marking Scheme" : "View Answer & Marking Scheme"}
          </button>
        )}
      </div>

      {showAnswer && question.answer && (
        <div className="bg-slate-50 p-5 border-t border-border animate-in slide-in-from-top-2">
          
          <div className="space-y-4">
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Answer</h4>
              <div className="text-sm text-slate-800 bg-white p-3 rounded border border-slate-200 whitespace-pre-wrap">
                {question.answer.model_answer || question.answer.final_answer || question.answer.explanation || "Answer not available."}
              </div>
            </div>

            {question.marking_scheme && question.marking_scheme.length > 0 && (
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Marking Scheme</h4>
                <div className="bg-white rounded border border-slate-200 overflow-hidden">
                  {question.marking_scheme.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center p-3 text-sm border-b border-slate-100 last:border-0">
                      <span className="text-slate-700">{item.criteria}</span>
                      <span className="font-semibold text-slate-900 bg-slate-100 px-2 py-0.5 rounded text-xs">
                        {item.marks} {item.marks === 1 ? 'mark' : 'marks'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

        </div>
      )}
    </div>
  );
}
