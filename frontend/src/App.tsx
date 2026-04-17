import { FormEvent, useEffect, useRef, useState } from "react";
import { analyzeProfile, extractDocument, fetchReport, startInterview, submitAnswer } from "./api";
import type {
  AnswerEvaluation,
  DocumentExtractResponse,
  FinalReport,
  InterviewSession,
  ProfileAnalysis,
  Question
} from "./types";

declare global {
  interface Window {
    webkitSpeechRecognition?: new () => SpeechRecognition;
    SpeechRecognition?: new () => SpeechRecognition;
  }

  interface SpeechRecognition extends EventTarget {
    continuous: boolean;
    interimResults: boolean;
    lang: string;
    onresult: ((event: SpeechRecognitionEvent) => void) | null;
    onerror: ((event: Event) => void) | null;
    onend: (() => void) | null;
    start(): void;
    stop(): void;
  }

  interface SpeechRecognitionEvent extends Event {
    results: SpeechRecognitionResultList;
  }

  interface SpeechRecognitionResultList extends ArrayLike<SpeechRecognitionResult> {
    [index: number]: SpeechRecognitionResult;
  }

  interface SpeechRecognitionResult extends ArrayLike<SpeechRecognitionAlternative> {
    [index: number]: SpeechRecognitionAlternative;
    isFinal: boolean;
    length: number;
  }

  interface SpeechRecognitionAlternative {
    transcript: string;
    confidence: number;
  }
}

const sampleJD = `QA Automation Engineer
We need a QA engineer with 5+ years of experience in Java, Selenium, API testing, CI/CD, SQL, and test strategy. The engineer should be able to design automation frameworks, work with REST APIs, and collaborate with developers in an agile team.`;

const sampleResume = `Rahul Sharma
Senior QA Engineer with 5 years of experience in Java, Selenium, TestNG, SQL, and agile delivery. Built UI automation suites, integrated tests into Jenkins pipelines, and partnered with backend teams to validate release quality.`;

const scoreTone = (score: number) => {
  if (score >= 8) return "strong";
  if (score >= 6) return "steady";
  return "risk";
};

function App() {
  const [candidateName, setCandidateName] = useState("Rahul Sharma");
  const [roleTitle, setRoleTitle] = useState("QA Automation Engineer");
  const [jobDescription, setJobDescription] = useState(sampleJD);
  const [resume, setResume] = useState(sampleResume);
  const [profile, setProfile] = useState<ProfileAnalysis | null>(null);
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [report, setReport] = useState<FinalReport | null>(null);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [lastEvaluation, setLastEvaluation] = useState<AnswerEvaluation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [jobUpload, setJobUpload] = useState<DocumentExtractResponse | null>(null);
  const [resumeUpload, setResumeUpload] = useState<DocumentExtractResponse | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const jobFileInputRef = useRef<HTMLInputElement | null>(null);
  const resumeFileInputRef = useRef<HTMLInputElement | null>(null);

  const currentQuestion: Question | null =
    !session || session.status === "completed"
      ? null
      : session.questions[session.current_question_index] ?? null;

  useEffect(() => {
    return () => recognitionRef.current?.stop();
  }, []);

  const startVoiceCapture = () => {
    const SpeechRecognitionImpl =
      window.SpeechRecognition ?? window.webkitSpeechRecognition;

    if (!SpeechRecognitionImpl) {
      setError("Speech recognition is not available in this browser. Use text input for now.");
      return;
    }

    const recognition = new SpeechRecognitionImpl();
    recognition.lang = "en-US";
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0]?.transcript ?? "")
        .join(" ");
      setCurrentAnswer(transcript);
    };

    recognition.onerror = () => {
      setError("Voice capture failed. You can still continue with typed answers.");
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    setIsListening(true);
    recognition.start();
  };

  const stopVoiceCapture = () => {
    recognitionRef.current?.stop();
    setIsListening(false);
  };

  const handleAnalyze = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setReport(null);
    setSession(null);
    setLastEvaluation(null);
    try {
      const result = await analyzeProfile({
        role_title: roleTitle,
        job_description: jobDescription,
        resume
      });
      setProfile(result);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (
    file: File | undefined,
    target: "job" | "resume"
  ) => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const extracted = await extractDocument(file);
      if (target === "job") {
        setJobDescription(extracted.content);
        setJobUpload(extracted);
      } else {
        setResume(extracted.content);
        setResumeUpload(extracted);
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to read uploaded file");
    } finally {
      setLoading(false);
    }
  };

  const handleStartInterview = async () => {
    if (!profile) return;
    setLoading(true);
    setError(null);
    setCurrentAnswer("");
    try {
      const started = await startInterview({
        candidate_name: candidateName,
        profile
      });
      setSession(started);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to start interview");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!session || !currentAnswer.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const response = await submitAnswer(session.id, currentAnswer.trim());
      setSession(response.session);
      setLastEvaluation(response.evaluation);
      setCurrentAnswer("");
      if (response.report_ready) {
        const finalReport = await fetchReport(session.id);
        setReport(finalReport);
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to submit answer");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <div className="hero-panel">
        <div className="hero-copy">
          <span className="eyebrow">System Brain</span>
          <h1>AI Interview Engine</h1>
          <p>
            Analyze the JD and resume, generate adaptive questions, run a live interview,
            score each answer, and finish with a hiring-ready report.
          </p>
        </div>
        <div className="hero-metrics">
          <article>
            <strong>5</strong>
            <span>AI modules</span>
          </article>
          <article>
            <strong>5</strong>
            <span>adaptive questions</span>
          </article>
          <article>
            <strong>4</strong>
            <span>weighted score factors</span>
          </article>
        </div>
      </div>

      <main className="grid">
        <section className="panel form-panel">
          <h2>1. Setup Interview</h2>
          <form onSubmit={handleAnalyze}>
            <label>
              Candidate name
              <input value={candidateName} onChange={(event) => setCandidateName(event.target.value)} />
            </label>
            <label>
              Role title
              <input value={roleTitle} onChange={(event) => setRoleTitle(event.target.value)} />
            </label>
            <label>
              Job description
              <div className="upload-row">
                <button
                  className="secondary"
                  type="button"
                  onClick={() => jobFileInputRef.current?.click()}
                  disabled={loading}
                >
                  Browse JD File
                </button>
                <input
                  ref={jobFileInputRef}
                  className="hidden-input"
                  type="file"
                  accept=".txt,.md,.pdf,.docx"
                  onChange={(event) => handleFileUpload(event.target.files?.[0], "job")}
                />
                {jobUpload ? (
                  <span className="upload-meta">
                    {jobUpload.filename} • {jobUpload.word_count} words
                  </span>
                ) : (
                  <span className="upload-meta">Upload .txt, .md, .pdf, or .docx</span>
                )}
              </div>
              <textarea
                rows={8}
                value={jobDescription}
                onChange={(event) => setJobDescription(event.target.value)}
              />
            </label>
            <label>
              Candidate resume
              <div className="upload-row">
                <button
                  className="secondary"
                  type="button"
                  onClick={() => resumeFileInputRef.current?.click()}
                  disabled={loading}
                >
                  Browse Resume
                </button>
                <input
                  ref={resumeFileInputRef}
                  className="hidden-input"
                  type="file"
                  accept=".txt,.md,.pdf,.docx"
                  onChange={(event) => handleFileUpload(event.target.files?.[0], "resume")}
                />
                {resumeUpload ? (
                  <span className="upload-meta">
                    {resumeUpload.filename} • {resumeUpload.word_count} words extracted
                  </span>
                ) : (
                  <span className="upload-meta">Upload .txt, .md, .pdf, or .docx</span>
                )}
              </div>
              <textarea rows={8} value={resume} onChange={(event) => setResume(event.target.value)} />
            </label>
            <button className="primary" type="submit" disabled={loading}>
              {loading ? "Analyzing..." : "Analyze JD + Resume"}
            </button>
          </form>
          {error ? <p className="error-banner">{error}</p> : null}
        </section>

        <section className="panel">
          <h2>2. Profile Analysis</h2>
          {!profile ? (
            <p className="empty-state">Run the analysis to extract skills, gaps, and match confidence.</p>
          ) : (
            <>
              <div className="stat-strip">
                <div>
                  <span>Experience match</span>
                  <strong>{profile.experience_match_percent}%</strong>
                </div>
                <div>
                  <span>Role</span>
                  <strong>{profile.role_title}</strong>
                </div>
              </div>
              <p className="summary">{profile.experience_summary}</p>
              <div className="tag-columns">
                <div>
                  <h3>Required</h3>
                  <div className="tags">{profile.required_skills.map(renderTag)}</div>
                </div>
                <div>
                  <h3>Candidate</h3>
                  <div className="tags">{profile.candidate_skills.map(renderTag)}</div>
                </div>
                <div>
                  <h3>Gaps</h3>
                  <div className="tags">{profile.gap_skills.length ? profile.gap_skills.map(renderTag) : <span className="soft">No major gaps</span>}</div>
                </div>
              </div>
              <button className="primary" onClick={handleStartInterview} disabled={loading}>
                Start Live Interview
              </button>
            </>
          )}
        </section>

        <section className="panel interview-panel">
          <h2>3. Live Interview</h2>
          {!session ? (
            <p className="empty-state">Start an interview to begin the adaptive question flow.</p>
          ) : report ? (
            <div className="report-panel">
              <div className="report-score">
                <span>Overall Score</span>
                <strong>{report.overall_score}/10</strong>
                <em>{report.recommendation}</em>
              </div>
              <p className="summary">{report.summary}</p>
              <div className="score-grid">
                {[
                  ["Technical", report.technical_score],
                  ["Communication", report.communication_score],
                  ["Confidence", report.confidence_score],
                  ["Relevance", report.relevance_score]
                ].map(([label, score]) => (
                  <div className="score-card" key={label}>
                    <span>{label}</span>
                    <strong>{score}</strong>
                  </div>
                ))}
              </div>
              <div className="tag-columns">
                <div>
                  <h3>Strengths</h3>
                  <div className="tags">{report.strengths.map(renderTag)}</div>
                </div>
                <div>
                  <h3>Weaknesses</h3>
                  <div className="tags">{report.weaknesses.map(renderTag)}</div>
                </div>
              </div>
            </div>
          ) : (
            <>
              <div className="question-card">
                <div className="question-meta">
                  <span>{currentQuestion?.category}</span>
                  <span>{currentQuestion?.difficulty}</span>
                  <span>{session.current_question_index + 1} / {session.questions.length}</span>
                </div>
                <h3>{currentQuestion?.text}</h3>
                <p className="soft">Target skill: {currentQuestion?.target_skill}</p>
              </div>

              <label>
                Candidate answer
                <textarea
                  rows={8}
                  value={currentAnswer}
                  onChange={(event) => setCurrentAnswer(event.target.value)}
                  placeholder="Type the answer or use voice capture..."
                />
              </label>

              <div className="button-row">
                {!isListening ? (
                  <button className="secondary" type="button" onClick={startVoiceCapture}>
                    Start Voice Capture
                  </button>
                ) : (
                  <button className="secondary alt" type="button" onClick={stopVoiceCapture}>
                    Stop Voice Capture
                  </button>
                )}
                <button className="primary" type="button" onClick={handleSubmitAnswer} disabled={loading}>
                  {loading ? "Scoring..." : "Submit Answer"}
                </button>
              </div>

              {lastEvaluation ? (
                <div className={`evaluation-card ${scoreTone(lastEvaluation.score)}`}>
                  <div className="evaluation-head">
                    <strong>Latest answer score: {lastEvaluation.score}/10</strong>
                    <span>{lastEvaluation.follow_up_direction} next-step</span>
                  </div>
                  <p>{lastEvaluation.feedback}</p>
                  <p className="soft">Improve: {lastEvaluation.improvement_tip}</p>
                </div>
              ) : null}
            </>
          )}
        </section>
      </main>
    </div>
  );
}

function renderTag(value: string) {
  return (
    <span className="tag" key={value}>
      {value}
    </span>
  );
}

export default App;
