import type { DocumentResponse, GenerationRequest, GenerationResponse } from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

export async function uploadDocument(file: File): Promise<DocumentResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/documents`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload Error: ${response.statusText}`);
  }

  return response.json();
}

export async function getDocumentStatus(documentId: string): Promise<DocumentResponse> {
  const response = await fetch(`${API_BASE}/documents/${documentId}/status`, {
    method: "GET",
  });

  if (!response.ok) {
    throw new Error(`Status Error: ${response.statusText}`);
  }

  return response.json();
}

export async function generateQuestions(request: GenerationRequest): Promise<GenerationResponse> {
  const response = await fetch(`${API_BASE}/generations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    let errorMsg = response.statusText;
    try {
      const errJson = await response.json();
      if (errJson.detail && errJson.detail.message) {
        errorMsg = errJson.detail.message;
      } else if (errJson.detail && typeof errJson.detail === "string") {
        errorMsg = errJson.detail;
      }
    } catch (e) {
      // ignore
    }
    throw new Error(`Generation Error: ${errorMsg}`);
  }

  return response.json();
}
