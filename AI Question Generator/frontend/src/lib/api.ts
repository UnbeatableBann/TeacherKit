import type { DocumentResponse, GenerationRequest, GenerationResponse } from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

export async function uploadDocument(
  file: File,
  onProgress?: (progress: number) => void
): Promise<DocumentResponse> {
  return new Promise((resolve, reject) => {
    const formData = new FormData();
    formData.append("file", file);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_BASE}/documents/process`);

    // Track upload progress
    if (xhr.upload && onProgress) {
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percentComplete = Math.round((event.loaded / event.total) * 100);
          onProgress(percentComplete);
        }
      };
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          resolve(response);
        } catch (err) {
          reject(new Error("Failed to parse JSON response"));
        }
      } else {
        reject(new Error(`Upload Error: ${xhr.statusText || xhr.status}`));
      }
    };

    xhr.onerror = () => {
      reject(new Error("Network Error occurred during upload"));
    };

    xhr.send(formData);
  });
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
