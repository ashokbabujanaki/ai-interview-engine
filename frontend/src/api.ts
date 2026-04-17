import type {
  AnswerResponse,
  DocumentExtractResponse,
  FinalReport,
  InterviewSession,
  ProfileAnalysis
} from "./types";

const API_BASE = "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json"
    },
    ...init
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail ?? "Request failed");
  }

  return response.json() as Promise<T>;
}

export function analyzeProfile(payload: {
  role_title: string;
  job_description: string;
  resume: string;
}) {
  return request<ProfileAnalysis>("/analyze-profile", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function startInterview(payload: {
  candidate_name: string;
  profile: ProfileAnalysis;
}) {
  return request<InterviewSession>("/interviews/start", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function submitAnswer(sessionId: string, answer: string) {
  return request<AnswerResponse>(`/interviews/${sessionId}/answer`, {
    method: "POST",
    body: JSON.stringify({ answer })
  });
}

export function fetchReport(sessionId: string) {
  return request<FinalReport>(`/interviews/${sessionId}/report`);
}

export async function extractDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/documents/extract`, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(error.detail ?? "Upload failed");
  }

  return response.json() as Promise<DocumentExtractResponse>;
}
