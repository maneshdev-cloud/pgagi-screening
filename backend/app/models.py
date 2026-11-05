"""Tables: roles, candidate resumes, interview sessions, Q&A turns."""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .db import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    title = Column(String(120), unique=True, nullable=False)
    description = Column(Text, default="")
    # comma separated topic tags + skills the role cares about
    focus_topics = Column(String(400), default="")
    key_skills = Column(String(400), default="")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True)
    candidate_name = Column(String(120), default="Candidate")
    raw_text = Column(Text, nullable=False)
    skills = Column(Text, default="")        # JSON list
    technologies = Column(Text, default="")  # JSON list
    domains = Column(Text, default="")       # JSON list
    created_at = Column(DateTime, default=datetime.utcnow)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    status = Column(String(20), default="in_progress")  # in_progress | completed
    current_index = Column(Integer, default=0)
    plan = Column(Text, default="")     # JSON: the generated question plan
    summary = Column(Text, default="")  # JSON: filled on finish
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume")
    role = relationship("Role")
    turns = relationship("Turn", back_populates="session", order_by="Turn.index")


class Turn(Base):
    __tablename__ = "turns"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    index = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    topic = Column(String(120), default="")
    source_chunk = Column(String(200), default="")   # KB chunk the question came from
    context_excerpt = Column(Text, default="")       # retrieved text shown as grounding
    answer = Column(Text, default="")
    is_followup = Column(Integer, default=0)

    session = relationship("Session", back_populates="turns")
