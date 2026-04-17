export type ProfileAnalysis = {
  role_title: string;
  required_skills: string[];
  candidate_skills: string[];
  gap_skills: string[];
  strengths: string[];
  experience_summary: string;
  experience_match_percent: number;
  recommended_focus_areas: string[];
};

export type DocumentExtractResponse = {
  filename: string;
  content: string;
  word_count: number;
};

export type Question = {
  id: string;
  category: "technical" | "behavioral" | "scenario";
  difficulty: "easy" | "medium" | "hard";
  text: string;
  target_skill: string;
  rationale: string;
};

export type AnswerEvaluation = {
  score: number;
  technical_accuracy: number;
  communication: number;
  confidence: number;
  relevance: number;
  feedback: string;
  improvement_tip: string;
  follow_up_direction: "simpler" | "deeper" | "lateral";
};

export type AnswerRecord = {
  question: Question;
  answer: string;
  evaluation: AnswerEvaluation;
};

export type InterviewSession = {
  id: string;
  candidate_name: string;
  status: "in_progress" | "completed";
  current_question_index: number;
  questions: Question[];
  answers: AnswerRecord[];
  profile: ProfileAnalysis;
};

export type AnswerResponse = {
  session: InterviewSession;
  evaluation: AnswerEvaluation;
  next_question?: Question | null;
  report_ready: boolean;
};

export type FinalReport = {
  session_id: string;
  candidate_name: string;
  technical_score: number;
  communication_score: number;
  confidence_score: number;
  relevance_score: number;
  overall_score: number;
  recommendation: "Reject" | "Hold" | "Next Round" | "Strong Hire";
  summary: string;
  strengths: string[];
  weaknesses: string[];
  gap_skills: string[];
  answer_breakdown: AnswerRecord[];
};
