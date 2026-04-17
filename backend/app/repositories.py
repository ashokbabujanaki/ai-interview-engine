from __future__ import annotations

from sqlalchemy.orm import Session, selectinload

from app.models import AnswerRecordModel, FinalReportModel, InterviewSessionModel
from app.schemas import (
    AnswerRecord,
    FinalReport,
    InterviewSession,
    ProfileAnalysis,
    Question,
)


def _row_to_session(row: InterviewSessionModel) -> InterviewSession:
    return InterviewSession(
        id=row.id,
        candidate_name=row.candidate_name,
        status=row.status,
        current_question_index=row.current_question_index,
        questions=[Question(**question) for question in row.questions_json],
        answers=[
            AnswerRecord(
                question=Question(**answer.question_json),
                answer=answer.answer_text,
                evaluation=answer.evaluation_json,
            )
            for answer in row.answers
        ],
        profile=ProfileAnalysis(**row.profile_json),
    )


def get_session(db: Session, session_id: str) -> InterviewSession | None:
    row = (
        db.query(InterviewSessionModel)
        .options(selectinload(InterviewSessionModel.answers))
        .filter(InterviewSessionModel.id == session_id)
        .one_or_none()
    )
    return _row_to_session(row) if row else None


def create_session(db: Session, session: InterviewSession) -> InterviewSession:
    row = InterviewSessionModel(
        id=session.id,
        candidate_name=session.candidate_name,
        status=session.status,
        current_question_index=session.current_question_index,
        profile_json=session.profile.model_dump(),
        questions_json=[question.model_dump() for question in session.questions],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return get_session(db, row.id) or session


def save_session(db: Session, session: InterviewSession) -> InterviewSession:
    row = (
        db.query(InterviewSessionModel)
        .options(selectinload(InterviewSessionModel.answers))
        .filter(InterviewSessionModel.id == session.id)
        .one()
    )
    row.candidate_name = session.candidate_name
    row.status = session.status
    row.current_question_index = session.current_question_index
    row.profile_json = session.profile.model_dump()
    row.questions_json = [question.model_dump() for question in session.questions]

    existing_by_sequence = {answer.sequence: answer for answer in row.answers}
    incoming_sequences = set()
    for sequence, record in enumerate(session.answers):
        incoming_sequences.add(sequence)
        answer_row = existing_by_sequence.get(sequence)
        if answer_row is None:
            answer_row = AnswerRecordModel(
                session_id=session.id,
                sequence=sequence,
                question_json=record.question.model_dump(),
                answer_text=record.answer,
                evaluation_json=record.evaluation.model_dump(),
            )
            row.answers.append(answer_row)
            continue

        answer_row.question_json = record.question.model_dump()
        answer_row.answer_text = record.answer
        answer_row.evaluation_json = record.evaluation.model_dump()

    for answer_row in list(row.answers):
        if answer_row.sequence not in incoming_sequences:
            db.delete(answer_row)

    db.commit()
    return get_session(db, session.id) or session


def save_report(db: Session, report: FinalReport) -> FinalReport:
    row = (
        db.query(FinalReportModel)
        .filter(FinalReportModel.session_id == report.session_id)
        .one_or_none()
    )
    if row is None:
        row = FinalReportModel(session_id=report.session_id, report_json=report.model_dump())
        db.add(row)
    else:
        row.report_json = report.model_dump()

    db.commit()
    return report


def get_report(db: Session, session_id: str) -> FinalReport | None:
    row = (
        db.query(FinalReportModel)
        .filter(FinalReportModel.session_id == session_id)
        .one_or_none()
    )
    return FinalReport(**row.report_json) if row else None
