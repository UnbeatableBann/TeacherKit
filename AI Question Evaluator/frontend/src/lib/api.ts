import type { EvaluationRequest, EvaluationResponse } from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "";

export async function evaluateAnswer(request: EvaluationRequest): Promise<EvaluationResponse> {
  const response = await fetch(`${API_BASE}/api/v1/evaluations`, {
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
