"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Role = { id: number; title: string; description: string; key_skills: string[] };
type Profile = { skills: string[]; technologies: string[]; domains: string[]; all_skills?: string[] };
type Turn = {
  index: number; question: string; topic: string; source_chunk: string;
  context_excerpt: string; answer: string; is_followup: boolean;
};
type SessionView = {
  id: number; status: string; candidate_name: string; role: string;
  profile: Profile; plan_query: string; total_questions: number;
  current_index: number; current_question: Turn | null; turns: Turn[];
  summary: null | {
    score: number; avg_grounding: number; avg_answer_words: number;
    topics: Record<string, { asked: number; grounding: number; words: number }>;
    insights: string[];
  };
};

export default function Home() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [samples, setSamples] = useState<{ name: string; text: string }[]>([]);
  const [name, setName] = useState("");
  const [roleId, setRoleId] = useState<number>(0);
  const [resumeText, setResumeText] = useState("");
  const [profile, setProfile] = useState<Profile | null>(null);
  const [session, setSession] = useState<SessionView | null>(null);
  const [answer, setAnswer] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API}/api/roles`).then((r) => r.json()).then((data) => {
      setRoles(data);
      if (data.length) setRoleId(data[0].id);
    }).catch(() => setError("Could not reach the backend API. Is it running on " + API + "?"));
    fetch(`${API}/api/samples`).then((r) => r.json()).then(setSamples).catch(() => {});
  }, []);

  async function parseText(text: string) {
    setResumeText(text);
    if (text.trim().length < 40) { setProfile(null); return; }
    const form = new FormData();
    form.append("text", text);
    const res = await fetch(`${API}/api/resumes/parse`, { method: "POST", body: form });
    if (res.ok) setProfile((await res.json()).profile);
  }

  async function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true); setError("");
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${API}/api/resumes/parse`, { method: "POST", body: form });
    setBusy(false);
    if (!res.ok) { setError("Could not parse that file. Try a text-based PDF or paste the text."); return; }
    const data = await res.json();
    setResumeText(data.text);
    setProfile(data.profile);
  }

  async function startSession() {
    setBusy(true); setError("");
    const res = await fetch(`${API}/api/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidate_name: name || "Candidate", role_id: roleId, resume_text: resumeText }),
    });
    setBusy(false);
    if (!res.ok) { setError((await res.json()).detail || "Could not start the session."); return; }
    setSession(await res.json());
  }

  async function submitAnswer() {
    if (!session || !answer.trim()) return;
    setBusy(true); setError("");
    const res = await fetch(`${API}/api/sessions/${session.id}/answers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer }),
    });
    setBusy(false);
    if (!res.ok) { setError("Could not save that answer."); return; }
    setAnswer("");
    setSession(await res.json());
  }

  async function finishEarly() {
    if (!session) return;
    const res = await fetch(`${API}/api/sessions/${session.id}/finish`, { method: "POST" });
    if (res.ok) setSession(await res.json());
  }

  return (
    <main>
      <h1>Role-Based Candidate Screening</h1>
      <p className="sub">
        Upload a resume, pick a role. The system parses the resume, retrieves matching
        knowledge-base material, and asks questions grounded in what it retrieved -
        then writes up a structured summary.
      </p>

      {!session && (
        <div className="card">
          <div className="row">
            <div>
              <label>Candidate name</label>
              <input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Aisha Khan" />
            </div>
            <div>
              <label>Role</label>
              <select value={roleId} onChange={(e) => setRoleId(Number(e.target.value))}>
                {roles.map((r) => <option key={r.id} value={r.id}>{r.title}</option>)}
              </select>
            </div>
          </div>

          <label>Resume file (PDF or text)</label>
          <input type="file" accept=".pdf,.txt,.md" onChange={onFile} />
          {samples.length > 0 && (
            <>
              <label>…or try a sample resume</label>
              <div>
                {samples.map((s) => (
                  <button key={s.name} type="button" className="ghost" style={{ marginRight: 8 }}
                    onClick={() => parseText(s.text)}>{s.name}</button>
                ))}
              </div>
            </>
          )}

          <label>Resume text</label>
          <textarea value={resumeText} onChange={(e) => parseText(e.target.value)}
            placeholder="Paste the resume text here, or upload a file above." />

          {profile && (
            <div style={{ marginTop: 12 }}>
              <div className="meta">Parsed profile</div>
              <div style={{ marginTop: 6 }}>
                {profile.skills.map((s) => <span key={s} className="chip">{s}</span>)}
                {profile.technologies.map((s) => <span key={s} className="chip">{s}</span>)}
                {profile.domains.map((s) => <span key={s} className="chip domain">{s}</span>)}
                {!profile.skills.length && !profile.technologies.length &&
                  <span className="meta">No known skills detected in this text yet.</span>}
              </div>
            </div>
          )}

          {error && <div className="err">{error}</div>}
          <button disabled={busy || resumeText.trim().length < 40 || !roleId} onClick={startSession}>
            {busy ? "Working…" : "Start screening session"}
          </button>
        </div>
      )}

      {session && session.status === "in_progress" && session.current_question && (
        <>
          <div className="card">
            <div className="meta">
              {session.candidate_name} · {session.role} · Question {session.current_index + 1}
            </div>
            <progress value={session.current_index} max={session.total_questions} />
            <div className="meta" style={{ marginTop: 10 }}>
              Topic: {session.current_question.topic}
              {session.current_question.is_followup ? " · follow-up" : ""}
            </div>
            <p className="q">{session.current_question.question}</p>
            <div className="grounding">
              <strong>Grounded in:</strong> {session.current_question.source_chunk}
              <br />{session.current_question.context_excerpt}…
            </div>
            <label>Your answer</label>
            <textarea value={answer} onChange={(e) => setAnswer(e.target.value)}
              placeholder="Answer in your own words. A detailed answer can earn a follow-up question." />
            {error && <div className="err">{error}</div>}
            <button disabled={busy || !answer.trim()} onClick={submitAnswer}>
              {busy ? "Saving…" : "Submit answer"}
            </button>{" "}
            <button className="ghost" onClick={finishEarly}>Finish session early</button>
          </div>

          {session.turns.filter((t) => t.answer).length > 0 && (
            <div className="card">
              <div className="meta">So far</div>
              {session.turns.filter((t) => t.answer).map((t) => (
                <div key={t.index} style={{ marginTop: 12 }}>
                  <div><strong>Q:</strong> {t.question}</div>
                  <div className="answer-prev"><strong>A:</strong> {t.answer}</div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {session && session.status === "completed" && session.summary && (
        <div className="card">
          <div className="meta">Session summary · {session.candidate_name} · {session.role}</div>
          <div className="score">{session.summary.score}<span style={{ fontSize: 18, color: "#9aa7bd" }}> / 100</span></div>
          <p className="meta">
            Average grounding {session.summary.avg_grounding} · average answer length{" "}
            {session.summary.avg_answer_words} words. Retrieval query used: “{session.plan_query}”
          </p>
          <table>
            <thead><tr><th>Topic</th><th>Questions</th><th>Grounding</th><th>Answer words</th></tr></thead>
            <tbody>
              {Object.entries(session.summary.topics).map(([topic, t]) => (
                <tr key={topic}><td>{topic}</td><td>{t.asked}</td><td>{t.grounding}</td><td>{t.words}</td></tr>
              ))}
            </tbody>
          </table>
          <div style={{ marginTop: 14 }}>
            <div className="meta">Insights</div>
            <ul>
              {session.summary.insights.map((i, idx) => <li key={idx}>{i}</li>)}
            </ul>
          </div>
          <button onClick={() => { setSession(null); setProfile(null); setResumeText(""); }}>
            Start a new session
          </button>
        </div>
      )}
    </main>
  );
}
