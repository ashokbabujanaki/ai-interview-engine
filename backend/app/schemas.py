from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ProfileAnalysisRequest(BaseModel):
    job_description: str = Field(min_length=40)
    resume: str = Field(min_length=40)
    role_title: str = Field(min_length=2)


class DocumentExtractResponse(BaseModel):
    model_config = {"from_attributes": True}

    filename: str
    content: str
    word_count: int


class ProfileAnalysis(BaseModel):
    model_config = {"from_attributes": True}

    role_title: str
    required_skills: list[str]
    candidate_skills: list[str]
    gap_skills: list[str]
    strengths: list[str]
    experience_summary: str
    experience_match_percent: int = Field(ge=0, le=100)
    recommended_focus_areas: list[str]


class Question(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    category: Literal["technical", "behavioral", "scenario"]
    difficulty: Literal["easy", "medium", "hard"]
    text: str
    target_skill: str
    rationale: str


class StartInterviewRequest(BaseModel):
    candidate_name: str = Field(min_length=2)
    profile: ProfileAnalysis


class AnswerRequest(BaseModel):
    answer: str = Field(min_length=2)


class AnswerEvaluation(BaseModel):
    model_config = {"from_attributes": True}

    score: int = Field(ge=1, le=10)
    technical_accuracy: int = Field(ge=1, le=10)
    communication: int = Field(ge=1, le=10)
    confidence: int = Field(ge=1, le=10)
    relevance: int = Field(ge=1, le=10)
    feedback: str
    improvement_tip: str
    follow_up_direction: Literal["simpler", "deeper", "lateral"]


class AnswerRecord(BaseModel):
    model_config = {"from_attributes": True}

    question: Question
    answer: str
    evaluation: AnswerEvaluation


class InterviewSession(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    candidate_name: str
    status: Literal["in_progress", "completed"]
    current_question_index: int = 0
    questions: list[Question]
    answers: list[AnswerRecord] = Field(default_factory=list)
    profile: ProfileAnalysis


class AnswerResponse(BaseModel):
    model_config = {"from_attributes": True}

    session: InterviewSession
    evaluation: AnswerEvaluation
    next_question: Question | None = None
    report_ready: bool = False


class FinalReport(BaseModel):
    model_config = {"from_attributes": True}

    session_id: str
    candidate_name: str
    technical_score: float
    communication_score: float
    confidence_score: float
    relevance_score: float
    overall_score: float
    recommendation: Literal["Reject", "Hold", "Next Round", "Strong Hire"]
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    gap_skills: list[str]
    answer_breakdown: list[AnswerRecord]
