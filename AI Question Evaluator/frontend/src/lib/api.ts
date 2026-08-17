import type { EvaluationRequest, EvaluationResponse } from "../types";

export async function evaluateAnswer(request: EvaluationRequest): Promise<EvaluationResponse> {
  const response = await fetch("/api/v1/evaluations", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}
