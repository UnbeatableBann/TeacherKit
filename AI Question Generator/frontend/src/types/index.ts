export interface DocumentResponse {
  document_id: string;
  filename: string;
  status: "uploaded" | "processing" | "ready" | "failed" | "uploading";
  uploadProgress?: number;
}

export interface MarkingSchemeItem {
  criteria: string;
  marks: number;
}

export interface AnswerSchema {
  correct_option?: string;
  explanation?: string;
  final_answer?: any;
  unit?: string;
  solution_steps?: string[];
  model_answer?: string;
  key_points?: string[];
}

export interface GeneratedQuestionResponse {
  id: string;
  question_text: string;
  topic?: string;
  question_type?: string;
  difficulty?: string;
  marks?: number;
  answer?: AnswerSchema;
  marking_scheme?: MarkingSchemeItem[];
  validation_status: string;
}

export interface GenerationRequest {
  document_ids: string[];
  subject: string;
  class_level: string;
  total_questions: number;
  requested_topic?: string;
  requested_difficulty?: "Easy" | "Medium" | "Hard";
}

export interface GenerationResponse {
  generation_id: string;
  status: string;
  subject: string;
  class_level: string;
  requested_count: number;
  generated_count: number;
  questions: GeneratedQuestionResponse[];
}

