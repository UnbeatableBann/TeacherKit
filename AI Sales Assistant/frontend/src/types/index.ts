export interface RequirementSchema {
  category: string | null;
  features_wanted: string[];
  budget_min: number | null;
  budget_max: number | null;
  preferences: string[];
  urgency: string | null;
}

export interface ObjectionSchema {
  type: string;
  text: string;
  status: string;
}

export interface RecommendationSchema {
  product_id: string;
  name: string;
  price: number;
  matched_features: string[];
  reasoning: string;
  confidence: number;
}

export interface AnsweredQuestionSchema {
  question: string;
  answer: string;
  source_product_ids: string[];
}

export interface LeadScoreSchema {
  score: number;
  breakdown: Record<string, string | number>;
}

export interface NextBestActionSchema {
  action: string;
  reason: string;
}

export interface EscalationSchema {
  triggered: boolean;
  reason: string | null;
}

export interface OrchestratorResponse {
  intent: string | null;
  requirements: RequirementSchema;
  objections: ObjectionSchema[];
  recommendations: RecommendationSchema[];
  answered_questions: AnsweredQuestionSchema[];
  unanswerable_questions: string[];
  lead_score: LeadScoreSchema;
  next_best_action: NextBestActionSchema;
  conversation_summary: string | null;
  escalation: EscalationSchema;
}

export interface LeadItem {
  conversation_id: string;
  customer_name: string;
  score: number;
  last_activity: string;
}
