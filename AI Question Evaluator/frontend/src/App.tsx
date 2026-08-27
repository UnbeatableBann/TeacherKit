import { useState } from 'react';
import { Header } from '@/components/layout/Header';
import { EvaluationForm } from '@/components/evaluation/EvaluationForm';
import { EvaluationResult } from '@/components/evaluation/EvaluationResult';
import { evaluateAnswer } from '@/lib/api';
import type { EvaluationRequest, EvaluationResponse } from '@/types';
import { AlertCircle } from 'lucide-react';

function App() {
  const [result, setResult] = useState<EvaluationResponse | null>(null);
  const [request, setRequest] = useState<EvaluationRequest | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEvaluate = async (evaluationRequest: EvaluationRequest) => {
    setIsLoading(true);
    setError(null);
    setRequest(evaluationRequest);
    setResult(null);
    
    try {
      const response = await evaluateAnswer(evaluationRequest);
      setResult(response);
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "An unexpected error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen animated-gradient-bg flex flex-col">
      <Header />
      <main className="flex-1">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8 space-y-8">
          
          <div className="flex flex-col md:flex-row gap-8 items-start">
            <div className="w-full md:w-5/12 shrink-0 sticky top-8">
              <EvaluationForm onSubmit={handleEvaluate} isLoading={isLoading} />
            </div>

            <div className="w-full md:w-7/12">
              {error && (
                <div className="bg-error-bg border border-error-border rounded-lg p-6 flex items-start gap-3 animate-in fade-in duration-300">
                  <AlertCircle className="h-6 w-6 text-error shrink-0" />
                  <div>
                    <h3 className="font-semibold text-error mb-1">Evaluation Failed</h3>
                    <p className="text-error/90 text-sm">We couldn't complete the evaluation. Please check your connection or try again. {error}</p>
                  </div>
                </div>
              )}

              {!result && !error && !isLoading && (
                <div className="h-64 flex flex-col items-center justify-center border border-dashed border-border rounded-lg bg-card/50 text-muted-foreground text-sm p-6 text-center animate-in fade-in duration-500">
                  <p>Submit an answer to see a structured evaluation.</p>
                </div>
              )}

              {isLoading && (
                <div className="space-y-6 animate-pulse">
                  <div className="h-32 bg-card border border-border rounded-lg"></div>
                  <div className="h-4 bg-muted rounded w-1/4"></div>
                  <div className="h-20 bg-card border border-border rounded-lg"></div>
                  <div className="h-4 bg-muted rounded w-1/3"></div>
                  <div className="h-20 bg-card border border-border rounded-lg"></div>
                </div>
              )}

              {result && request && !isLoading && (
                <EvaluationResult result={result} request={request} />
              )}
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

export default App;
