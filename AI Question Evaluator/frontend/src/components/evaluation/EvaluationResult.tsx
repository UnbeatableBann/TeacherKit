import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, XCircle, AlertCircle, AlertTriangle } from "lucide-react";
import type { EvaluationResponse, EvaluationRequest } from "@/types";

interface EvaluationResultProps {
  result: EvaluationResponse;
  request: EvaluationRequest;
}

export function EvaluationResult({ result, request }: EvaluationResultProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "correct":
        return <CheckCircle2 className="h-6 w-6 text-[#15803D]" />;
      case "partially_correct":
        return <AlertTriangle className="h-6 w-6 text-[#B45309]" />;
      case "incorrect":
        return <XCircle className="h-6 w-6 text-[#B91C1C]" />;
      case "evaluation_failure":
        return <AlertCircle className="h-6 w-6 text-[#B91C1C]" />;
      default:
        return <AlertCircle className="h-6 w-6 text-muted-foreground" />;
    }
  };

  const getStatusText = (status: string) => {
    return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "correct":
        return "success";
      case "partially_correct":
        return "warning";
      case "incorrect":
        return "destructive";
      default:
        return "secondary";
    }
  };

  const color = result.status === "correct" ? "#15803D" : result.status === "partially_correct" ? "#B45309" : "#B91C1C";

  return (
    <div className="space-y-6">
      <Card className="glass-panel overflow-hidden border-t-4" style={{ borderTopColor: color }}>
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-sm font-medium text-muted-foreground mb-1">Score</h2>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold tracking-tight text-foreground">
                  {result.score !== null ? result.score.toFixed(1) : "—"}
                </span>
                <span className="text-xl text-muted-foreground font-medium">/ 100</span>
              </div>
            </div>
            <div className="flex flex-col items-start sm:items-end gap-2">
              <h2 className="text-sm font-medium text-muted-foreground hidden sm:block">Status</h2>
              <div className="flex items-center gap-2">
                {getStatusIcon(result.status)}
                <Badge variant={getStatusBadge(result.status) as any} className="text-sm px-3 py-1">
                  {getStatusText(result.status)}
                </Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-6 text-sm">
        <section>
          <h3 className="font-semibold text-foreground border-b border-border pb-2 mb-3">Question</h3>
          <p className="text-secondary-foreground">{request.question.text}</p>
        </section>

        <section>
          <h3 className="font-semibold text-foreground border-b border-border pb-2 mb-3">Student Answer</h3>
          <p className="text-secondary-foreground bg-secondary/50 p-4 rounded-md border border-border">{request.student_answer.content}</p>
        </section>

        <section>
          <h3 className="font-semibold text-foreground border-b border-border pb-2 mb-3">Evaluation</h3>
          <p className="text-secondary-foreground">{result.feedback.explanation}</p>
        </section>

        {result.concept_analysis.correct.length > 0 && (
          <section>
            <h3 className="font-semibold text-[#15803D] border-b border-border pb-2 mb-3">What you got right</h3>
            <ul className="space-y-2">
              {result.concept_analysis.correct.map((concept, i) => (
                <li key={i} className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-[#15803D] mt-0.5 shrink-0" />
                  <span className="text-secondary-foreground">{concept}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        {result.concept_analysis.missing.length > 0 && (
          <section>
            <h3 className="font-semibold text-[#B45309] border-b border-border pb-2 mb-3">What is missing</h3>
            <ul className="space-y-2">
              {result.concept_analysis.missing.map((concept, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-[#B45309] mt-2 shrink-0" />
                  <span className="text-secondary-foreground">{concept}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        {result.error_analysis.subject_mismatch && (
          <section>
            <h3 className="font-semibold text-[#B45309] border-b border-border pb-2 mb-3">Subject Irrelevance</h3>
            <div className="bg-[#FEF9C3] border border-[#FEF08A] rounded-md p-4">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="h-4 w-4 text-[#B45309]" />
                <span className="font-medium text-[#B45309]">
                  Question Irrelevant to Selected Subject
                </span>
              </div>
              <p className="text-sm text-[#713F12] mt-2">The content of this question does not appear to match the selected subject category. The evaluation below might be flawed due to missing subject-specific context.</p>
            </div>
          </section>
        )}

        {result.error_analysis.error_type && (
          <section>
            <h3 className="font-semibold text-[#B91C1C] border-b border-border pb-2 mb-3">Issues identified</h3>
            <div className="bg-[#FEF2F2] border border-[#FECACA] rounded-md p-4">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="h-4 w-4 text-[#B91C1C]" />
                <span className="font-medium text-[#B91C1C]">
                  {getStatusText(result.error_analysis.error_type)}
                </span>
                <Badge variant="outline" className="ml-2 text-xs border-[#FECACA] text-[#B91C1C]">
                  {result.error_analysis.severity}
                </Badge>
              </div>
              {result.error_analysis.explanation && (
                <p className="text-sm text-[#991B1B] mt-2">{result.error_analysis.explanation}</p>
              )}
            </div>
          </section>
        )}

        {result.feedback.improvement_hint && (
          <section>
            <h3 className="font-semibold text-foreground border-b border-border pb-2 mb-3">How to improve</h3>
            <p className="text-secondary-foreground bg-accent p-4 rounded-md border border-border">
              {result.feedback.improvement_hint}
            </p>
          </section>
        )}

        <section>
          <h3 className="font-semibold text-muted-foreground border-b border-border pb-2 mb-3">Reference Answer</h3>
          <p className="text-muted-foreground">{request.reference_answer.text}</p>
        </section>
      </div>
    </div>
  );
}
