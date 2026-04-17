from sqlalchemy.orm import Session

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import Base, engine, get_db
from app import models  # noqa: F401
from app.repositories import create_session as create_session_record
from app.repositories import get_report as get_report_record
from app.repositories import get_session as get_session_record
from app.repositories import save_report, save_session
from app.schemas import (
    AnswerRequest,
    AnswerResponse,
    DocumentExtractResponse,
    FinalReport,
    InterviewSession,
    ProfileAnalysis,
    ProfileAnalysisRequest,
    StartInterviewRequest,
)
from app.services.document_parser import extract_document_text
from app.services.interview_engine import (
    analyze_profile,
    append_answer,
    build_report,
    create_session as create_interview_session,
)

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/analyze-profile", response_model=ProfileAnalysis)
def analyze_profile_endpoint(payload: ProfileAnalysisRequest) -> ProfileAnalysis:
    return analyze_profile(
        role_title=payload.role_title,
        job_description=payload.job_description,
        resume=payload.resume,
    )


@app.post("/api/v1/documents/extract", response_model=DocumentExtractResponse)
async def extract_document(file: UploadFile = File(...)) -> DocumentExtractResponse:
    content = await extract_document_text(file)
    if len(content) < 20:
        raise HTTPException(
            status_code=400,
            detail="The file was read, but not enough text was extracted. Try a clearer text-based file.",
        )
    return DocumentExtractResponse(
        filename=file.filename or "uploaded-file",
        content=content,
        word_count=len(content.split()),
    )


@app.post("/api/v1/interviews/start", response_model=InterviewSession)
def start_interview(
    payload: StartInterviewRequest,
    db: Session = Depends(get_db),
) -> InterviewSession:
    session = create_interview_session(payload.candidate_name, payload.profile)
    return create_session_record(db, session)


@app.get("/api/v1/interviews/{session_id}", response_model=InterviewSession)
def get_interview(session_id: str, db: Session = Depends(get_db)) -> InterviewSession:
    session = get_session_record(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return session


@app.post("/api/v1/interviews/{session_id}/answer", response_model=AnswerResponse)
def answer_question(
    session_id: str,
    payload: AnswerRequest,
    db: Session = Depends(get_db),
) -> AnswerResponse:
    session = get_session_record(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Interview already completed")

    evaluation = append_answer(session, payload.answer)
    session = save_session(db, session)
    if session.status == "completed":
        save_report(db, build_report(session))
    next_question = (
        session.questions[session.current_question_index]
        if session.status == "in_progress"
        else None
    )
    return AnswerResponse(
        session=session,
        evaluation=evaluation,
        next_question=next_question,
        report_ready=session.status == "completed",
    )


@app.get("/api/v1/interviews/{session_id}/report", response_model=FinalReport)
def get_report(session_id: str, db: Session = Depends(get_db)) -> FinalReport:
    session = get_session_record(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Interview is still in progress")
    persisted_report = get_report_record(db, session_id)
    if persisted_report:
        return persisted_report
    report = build_report(session)
    save_report(db, report)
    return report
