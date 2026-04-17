from __future__ import annotations

import re
import uuid
from statistics import mean

from app.schemas import (
    AnswerEvaluation,
    AnswerRecord,
    FinalReport,
    InterviewSession,
    ProfileAnalysis,
    Question,
)
from app.services.ai_client import ai_client

QUESTION_COUNT = 5

SKILL_TAXONOMY = [
    ".net",
    "c#",
    "asp.net",
    "spring boot",
    "hibernate",
    "maven",
    "gradle",
    "sap",
    "sap mm",
    "sap ecc",
    "sap s/4hana",
    "s/4hana",
    "procurement",
    "procure-to-pay",
    "p2p",
    "inventory management",
    "inventory",
    "valuation",
    "account determination",
    "invoice verification",
    "logistic invoice verification",
    "gr/ir",
    "goods receipt",
    "goods issue",
    "stock transfer",
    "stock movements",
    "transfer posting",
    "physical inventory",
    "cycle counting",
    "purchase requisition",
    "purchase order",
    "scheduling agreement",
    "outline agreement",
    "contract management",
    "release strategy",
    "vendor master",
    "material master",
    "source list",
    "info record",
    "pricing procedure",
    "valuation class",
    "movement types",
    "mm-fi integration",
    "mm-sd integration",
    "mm-pp integration",
    "sd integration",
    "finance integration",
    "cross-company",
    "intercompany",
    "lsmw",
    "idocs",
    "bapis",
    "batch management",
    "serial number management",
    "split valuation",
    "special stock",
    "warehouse management",
    "ewm",
    "rf framework",
    "putaway",
    "picking",
    "replenishment",
    "yard management",
    "cross-docking",
    "fit-to-standard",
    "uat",
    "cutover",
    "blueprint",
    "functional specification",
    "sop",
    "qa automation",
    "automation testing",
    "manual testing",
    "regression testing",
    "smoke testing",
    "ui testing",
    "functional testing",
    "test strategy",
    "test planning",
    "bdd",
    "cucumber",
    "rest assured",
    "soapui",
    "jmeter",
    "performance testing",
    "load testing",
    "jenkins",
    "java",
    "python",
    "javascript",
    "typescript",
    "react",
    "node.js",
    "fastapi",
    "selenium",
    "playwright",
    "cypress",
    "api testing",
    "rest",
    "postman",
    "sql",
    "aws",
    "docker",
    "kubernetes",
    "terraform",
    "ansible",
    "helm",
    "argocd",
    "azure devops",
    "github actions",
    "gitlab ci",
    "linux",
    "bash",
    "shell scripting",
    "monitoring",
    "prometheus",
    "grafana",
    "elk",
    "splunk",
    "ci/cd",
    "pytest",
    "testng",
    "junit",
    "agile",
    "microservices",
    "data engineering",
    "etl",
    "elt",
    "data pipelines",
    "spark",
    "pyspark",
    "hadoop",
    "airflow",
    "snowflake",
    "databricks",
    "kafka",
    "bigquery",
    "redshift",
    "dbt",
    "oracle",
    "pl/sql",
    "mongodb",
    "postgresql",
    "mysql",
    "sql server",
    "nosql",
    "power bi",
    "tableau",
    "salesforce",
    "apex",
    "lightning",
    "lwc",
    "soql",
    "service cloud",
    "sales cloud",
    "servicenow",
    "workday",
]

DISPLAY_NAMES = {
    ".net": ".NET",
    "c#": "C#",
    "asp.net": "ASP.NET",
    "spring boot": "Spring Boot",
    "sap": "SAP",
    "sap mm": "SAP MM",
    "sap ecc": "SAP ECC",
    "sap s/4hana": "SAP S/4HANA",
    "s/4hana": "S/4HANA",
    "procure-to-pay": "Procure-to-Pay",
    "p2p": "P2P",
    "gr/ir": "GR/IR",
    "mm-fi integration": "MM-FI Integration",
    "mm-sd integration": "MM-SD Integration",
    "mm-pp integration": "MM-PP Integration",
    "sd integration": "SD Integration",
    "finance integration": "Finance Integration",
    "lsmw": "LSMW",
    "idocs": "IDOCs",
    "bapis": "BAPIs",
    "ewm": "EWM",
    "uat": "UAT",
    "sop": "SOP",
    "qa automation": "QA Automation",
    "bdd": "BDD",
    "cucumber": "Cucumber",
    "rest assured": "Rest Assured",
    "soapui": "SoapUI",
    "jmeter": "JMeter",
    "jenkins": "Jenkins",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "helm": "Helm",
    "argocd": "ArgoCD",
    "azure devops": "Azure DevOps",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",
    "linux": "Linux",
    "bash": "Bash",
    "prometheus": "Prometheus",
    "grafana": "Grafana",
    "elk": "ELK",
    "splunk": "Splunk",
    "ci/cd": "CI/CD",
    "node.js": "Node.js",
    "api testing": "API Testing",
    "rest": "REST",
    "sql": "SQL",
    "etl": "ETL",
    "elt": "ELT",
    "pyspark": "PySpark",
    "airflow": "Airflow",
    "snowflake": "Snowflake",
    "databricks": "Databricks",
    "kafka": "Kafka",
    "bigquery": "BigQuery",
    "redshift": "Redshift",
    "dbt": "dbt",
    "pl/sql": "PL/SQL",
    "mongodb": "MongoDB",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "sql server": "SQL Server",
    "nosql": "NoSQL",
    "power bi": "Power BI",
    "tableau": "Tableau",
    "salesforce": "Salesforce",
    "apex": "Apex",
    "lightning": "Lightning",
    "lwc": "LWC",
    "soql": "SOQL",
    "servicenow": "ServiceNow",
    "workday": "Workday",
}


def _normalize_skill(skill: str) -> str:
    cleaned = skill.strip().lower()
    aliases = {
        "api": "api testing",
        "rest api": "api testing",
        "restful services": "api testing",
        "node": "node.js",
        "sap materials management": "sap mm",
        "materials management": "sap mm",
        "sap mm consultant": "sap mm",
        "mm": "sap mm",
        "procure to pay": "procure-to-pay",
        "goods receipts": "goods receipt",
        "goods issues": "goods issue",
        "stock transfers": "stock transfer",
        "purchase requisitions": "purchase requisition",
        "purchase orders": "purchase order",
        "vendor masters": "vendor master",
        "material masters": "material master",
        "fit to standard": "fit-to-standard",
        "automation": "qa automation",
        "test automation": "qa automation",
        "api tests": "api testing",
        "restful api": "api testing",
        "dotnet": ".net",
        ".net core": ".net",
        "asp.net core": "asp.net",
        "c sharp": "c#",
        "springboot": "spring boot",
        "ado": "azure devops",
        "github action": "github actions",
        "gitlab": "gitlab ci",
        "shell": "shell scripting",
        "observability": "monitoring",
        "spark sql": "spark",
        "apache spark": "spark",
        "apache airflow": "airflow",
        "data factory": "data pipelines",
        "aws glue": "etl",
        "ms sql": "sql server",
        "mssql": "sql server",
        "sales force": "salesforce",
        "lightning web components": "lwc",
        "snowflake sql": "snowflake",
    }
    return aliases.get(cleaned, cleaned)


def _display_skill(skill: str) -> str:
    normalized = _normalize_skill(skill)
    return DISPLAY_NAMES.get(normalized, normalized.title())


def _extract_skills(text: str) -> list[str]:
    lowered = text.lower()
    found = []
    for skill in SKILL_TAXONOMY:
        if skill in lowered:
            found.append(_display_skill(skill))
    return sorted(set(found))


def _estimate_experience(text: str) -> int:
    match = re.search(r"(\d+)\+?\s+years?", text.lower())
    return int(match.group(1)) if match else 3


def analyze_profile(role_title: str, job_description: str, resume: str) -> ProfileAnalysis:
    schema = {
        "type": "object",
        "properties": {
            "required_skills": {"type": "array", "items": {"type": "string"}},
            "candidate_skills": {"type": "array", "items": {"type": "string"}},
            "gap_skills": {"type": "array", "items": {"type": "string"}},
            "strengths": {"type": "array", "items": {"type": "string"}},
            "experience_summary": {"type": "string"},
            "experience_match_percent": {"type": "integer"},
            "recommended_focus_areas": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "required_skills",
            "candidate_skills",
            "gap_skills",
            "strengths",
            "experience_summary",
            "experience_match_percent",
            "recommended_focus_areas",
        ],
        "additionalProperties": False,
    }
    prompt = f"""
You are an expert technical recruiter.
Analyze the job description and candidate resume for the role "{role_title}".
Return only JSON.

Job Description:
{job_description}

Resume:
{resume}
"""
    ai_result = ai_client.generate_json(prompt, "profile_analysis", schema)
    if ai_result:
        return ProfileAnalysis(role_title=role_title, **ai_result)

    required_skills = _extract_skills(job_description)
    candidate_skills = _extract_skills(resume)
    required_set = {_normalize_skill(skill) for skill in required_skills}
    candidate_set = {_normalize_skill(skill) for skill in candidate_skills}
    gap_skills = sorted(
        skill for skill in required_skills if _normalize_skill(skill) not in candidate_set
    )
    overlap = required_set.intersection(candidate_set)
    match_percent = int((len(overlap) / max(len(required_set), 1)) * 100)
    years = _estimate_experience(resume)

    return ProfileAnalysis(
        role_title=role_title,
        required_skills=required_skills or ["Problem Solving", "Communication"],
        candidate_skills=candidate_skills or ["General Engineering"],
        gap_skills=gap_skills,
        strengths=(candidate_skills[:3] or ["Transferable engineering experience"]),
        experience_summary=f"Candidate shows roughly {years} years of relevant experience based on the resume text.",
        experience_match_percent=match_percent,
        recommended_focus_areas=gap_skills[:3] or ["Hands-on scenarios", "Depth validation"],
    )


def generate_questions(profile: ProfileAnalysis) -> list[Question]:
    schema = {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "difficulty": {"type": "string"},
                        "text": {"type": "string"},
                        "target_skill": {"type": "string"},
                        "rationale": {"type": "string"},
                    },
                    "required": ["category", "difficulty", "text", "target_skill", "rationale"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["questions"],
        "additionalProperties": False,
    }
    prompt = f"""
You are a senior interviewer designing an adaptive interview.
Create {QUESTION_COUNT} interview questions for role "{profile.role_title}".
Required skills: {", ".join(profile.required_skills)}
Candidate strengths: {", ".join(profile.strengths)}
Candidate gaps: {", ".join(profile.gap_skills) or "None"}

Rules:
- Order questions easy to medium to hard.
- Mix technical, behavioral, and scenario questions.
- Focus on practical real-world questions, not definitions.
- Include likely target skill and a short rationale.
Return only JSON.
"""
    ai_result = ai_client.generate_json(prompt, "question_set", schema)
    if ai_result:
        return [
            Question(id=str(uuid.uuid4()), **item)
            for item in ai_result["questions"][:QUESTION_COUNT]
        ]

    skills = profile.required_skills or ["Problem Solving"]
    questions: list[Question] = []
    templates = [
        ("technical", "easy", "Walk me through how you have used {skill} in a recent project."),
        ("technical", "easy", "What failure patterns do you usually watch for when working with {skill}?"),
        ("behavioral", "medium", "Tell me about a time you had to unblock a delivery risk related to {skill}."),
        ("scenario", "medium", "A production issue appears in an area owned by {skill}. How would you investigate it?"),
        ("technical", "medium", "How do you measure quality and reliability when using {skill}?"),
    ]
    for index, template in enumerate(templates[:QUESTION_COUNT]):
        skill = skills[index % len(skills)]
        category, difficulty, text = template
        questions.append(
            Question(
                id=str(uuid.uuid4()),
                category=category,
                difficulty=difficulty,
                text=text.format(skill=skill),
                target_skill=skill,
                rationale=f"Validate practical ability in {skill}.",
            )
        )
    return questions


def evaluate_answer(question: Question, answer: str, profile: ProfileAnalysis) -> AnswerEvaluation:
    schema = {
        "type": "object",
        "properties": {
            "score": {"type": "integer"},
            "technical_accuracy": {"type": "integer"},
            "communication": {"type": "integer"},
            "confidence": {"type": "integer"},
            "relevance": {"type": "integer"},
            "feedback": {"type": "string"},
            "improvement_tip": {"type": "string"},
            "follow_up_direction": {"type": "string"},
        },
        "required": [
            "score",
            "technical_accuracy",
            "communication",
            "confidence",
            "relevance",
            "feedback",
            "improvement_tip",
            "follow_up_direction",
        ],
        "additionalProperties": False,
    }
    prompt = f"""
You are evaluating a candidate answer in an interview.
Role: {profile.role_title}
Question: {question.text}
Target skill: {question.target_skill}
Candidate answer: {answer}

Return only JSON.
Score each field from 1 to 10.
follow_up_direction must be one of: simpler, deeper, lateral.
"""
    ai_result = ai_client.generate_json(prompt, "answer_evaluation", schema)
    if ai_result:
        return AnswerEvaluation(**ai_result)

    answer_lower = answer.lower()
    words = len(answer.split())
    skill_tokens = question.target_skill.lower().replace("/", " ").split()
    keyword_hits = sum(1 for token in skill_tokens if token in answer_lower)
    structure_bonus = 1 if any(marker in answer_lower for marker in ["first", "then", "finally", "because"]) else 0
    detail_bonus = 2 if words > 60 else 1 if words > 25 else 0

    technical = min(10, max(3, 4 + keyword_hits + detail_bonus))
    communication = min(10, max(3, 4 + structure_bonus + (1 if words > 35 else 0)))
    confidence = min(10, max(3, 5 + (1 if "i" in answer_lower else 0) + (1 if words > 40 else 0)))
    relevance = min(10, max(3, 4 + keyword_hits + (1 if question.target_skill.lower() in answer_lower else 0)))
    weighted = round((technical * 0.4) + (communication * 0.2) + (confidence * 0.2) + (relevance * 0.2))

    if weighted <= 4:
        direction = "simpler"
        feedback = "The answer stays high level and needs more concrete examples or technical depth."
        tip = "Use a recent project example and explain the problem, approach, and outcome."
    elif weighted >= 8:
        direction = "deeper"
        feedback = "Strong answer with practical grounding and good structure."
        tip = "Add a measurable result or tradeoff to make the answer even more senior-level."
    else:
        direction = "lateral"
        feedback = "Solid baseline answer, but some parts would benefit from clearer depth or stronger specifics."
        tip = "Anchor the answer in one real scenario and explain why your approach worked."

    return AnswerEvaluation(
        score=weighted,
        technical_accuracy=technical,
        communication=communication,
        confidence=confidence,
        relevance=relevance,
        feedback=feedback,
        improvement_tip=tip,
        follow_up_direction=direction,
    )


def create_session(candidate_name: str, profile: ProfileAnalysis) -> InterviewSession:
    return InterviewSession(
        id=str(uuid.uuid4()),
        candidate_name=candidate_name,
        status="in_progress",
        questions=generate_questions(profile),
        profile=profile,
    )


def append_answer(session: InterviewSession, answer: str) -> AnswerEvaluation:
    current_question = session.questions[session.current_question_index]
    evaluation = evaluate_answer(current_question, answer, session.profile)
    session.answers.append(
        AnswerRecord(question=current_question, answer=answer, evaluation=evaluation)
    )
    session.current_question_index += 1
    if session.current_question_index >= len(session.questions):
        session.status = "completed"
    return evaluation


def build_report(session: InterviewSession) -> FinalReport:
    answer_breakdown = session.answers
    technical_scores = [record.evaluation.technical_accuracy for record in answer_breakdown] or [0]
    communication_scores = [record.evaluation.communication for record in answer_breakdown] or [0]
    confidence_scores = [record.evaluation.confidence for record in answer_breakdown] or [0]
    relevance_scores = [record.evaluation.relevance for record in answer_breakdown] or [0]
    overall_score = (
        mean(technical_scores) * 0.4
        + mean(communication_scores) * 0.2
        + mean(confidence_scores) * 0.2
        + mean(relevance_scores) * 0.2
    )

    if overall_score >= 8.5:
        recommendation = "Strong Hire"
    elif overall_score >= 7:
        recommendation = "Next Round"
    elif overall_score >= 5.5:
        recommendation = "Hold"
    else:
        recommendation = "Reject"

    strengths = sorted(
        {
            record.question.target_skill
            for record in answer_breakdown
            if record.evaluation.score >= 8
        }
    ) or session.profile.strengths
    weaknesses = sorted(
        {
            record.question.target_skill
            for record in answer_breakdown
            if record.evaluation.score <= 6
        }
    ) or session.profile.gap_skills

    summary = (
        f"{session.candidate_name} scored {overall_score:.1f}/10 overall for {session.profile.role_title}. "
        f"The interview shows stronger signals in {', '.join(strengths[:3]) or 'core execution'} "
        f"and improvement needs around {', '.join(weaknesses[:3]) or 'depth consistency'}."
    )

    return FinalReport(
        session_id=session.id,
        candidate_name=session.candidate_name,
        technical_score=round(mean(technical_scores), 1),
        communication_score=round(mean(communication_scores), 1),
        confidence_score=round(mean(confidence_scores), 1),
        relevance_score=round(mean(relevance_scores), 1),
        overall_score=round(overall_score, 1),
        recommendation=recommendation,
        summary=summary,
        strengths=strengths,
        weaknesses=weaknesses,
        gap_skills=session.profile.gap_skills,
        answer_breakdown=answer_breakdown,
    )
