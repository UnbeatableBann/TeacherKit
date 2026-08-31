export type Subject = "mathematics" | "science" | "english" | "history" | "general";
export type ClassLevel = "std_1" | "std_2" | "std_3" | "std_4" | "std_5" | "std_6" | "std_7" | "std_8" | "std_9" | "std_10" | "std_11" | "std_12" | "ug";
export type QuestionCategory = "objective" | "numerical" | "subjective";
export type QuestionType = "mcq" | "multiple_select" | "true_false" | "fill_in_the_blank" | "exact_answer" | "numeric" | "formula" | "unit_based" | "short_answer" | "explanation" | "descriptive" | "essay" | "proof" | "derivation";
export type EvaluationStatus = "correct" | "partially_correct" | "incorrect" | "insufficient_reference" | "unsupported" | "evaluation_failure";

export interface QuestionOption {
  id: string;
  text: string;
}

export interface Question {
  id: string;
  text: string;
  subject: Subject;
  class_level: ClassLevel;
  category: QuestionCategory;
  type: QuestionType;
  options?: QuestionOption[];
  marks?: number;
  expected_unit?: string;
}

export interface ReferenceAnswer {
  text?: string;
  accepted_answers?: string[];
  correct_option_ids?: string[];
  expected_concepts?: string[];
  expected_steps?: string[];
  rubric?: Record<string, number>;
}

export interface StudentAnswer {
  content: string;
  source?: "text";
}

export interface EvaluationRequest {
  question: Question;
  reference_answer: ReferenceAnswer;
  student_answer: StudentAnswer;
}

export interface Dimension {
  score: number;
  evidence: string[];
}

export interface ConceptAnalysis {
  correct: string[];
  missing: string[];
  incorrect: string[];
}

export interface ErrorAnalysis {
  error_type?: string;
  severity: "none" | "minor" | "major" | "critical";
  explanation?: string;
  distance_from_correct?: Record<string, any>;
  subject_mismatch?: boolean;
}

export interface Feedback {
  summary: string;
  explanation: string;
  improvement_hint?: string;
}

export interface EvaluationResponse {
  status: EvaluationStatus;
  score: number | null;
  confidence: number;
  dimensions: Record<string, Dimension>;
  concept_analysis: ConceptAnalysis;
  error_analysis: ErrorAnalysis;
  feedback: Feedback;
  metadata: Record<string, any>;
}
