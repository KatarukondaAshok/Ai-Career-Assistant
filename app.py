import os
import sys
import ast
import json
import asyncio
from pathlib import Path
from contextlib import AsyncExitStack
from typing import Any, Dict, List

# IMPORTANT: Windows fix for MCP stdio subprocess
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import fitz
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

# ---------------------------------------------------------
# ENV
# ---------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

# ---------------------------------------------------------
# Page setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: #0a0e1a;
        color: #e2e8f0;
    }

    .block-container {
        max-width: 1120px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    .hero {
        background: linear-gradient(135deg, #0f1929 0%, #1a1040 50%, #0a1628 100%);
        border: 1px solid #1e2d45;
        border-radius: 24px;
        padding: 34px 38px;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    }

    .hero-badge {
        display: inline-block;
        background: rgba(34, 211, 238, 0.10);
        border: 1px solid rgba(34, 211, 238, 0.25);
        color: #22d3ee;
        padding: 8px 14px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 16px;
    }

    .hero-title {
        font-size: 56px;
        font-weight: 800;
        line-height: 1.05;
        color: white;
        margin-bottom: 12px;
        letter-spacing: -1px;
    }

    .hero-sub {
        color: #9fb3d9;
        font-size: 21px;
        line-height: 1.7;
        max-width: 920px;
        margin-bottom: 0;
    }

    .panel-title {
        color: #00d4ff;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .panel-sub {
        color: #94a3b8;
        font-size: 15px;
        margin-bottom: 18px;
    }

    .result-card {
        background: #0f1929;
        border: 1px solid #1e2d45;
        border-radius: 16px;
        padding: 18px;
        margin-top: 18px;
    }

    .result-title {
        color: #10b981;
        font-size: 13px;
        font-family: monospace;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
        border-bottom: 1px solid #1e2d45;
        padding-bottom: 10px;
    }

    .result-card h3 {
        color: #22d3ee;
        margin-top: 14px;
        margin-bottom: 8px;
        font-size: 20px;
    }

    .result-card ul {
        padding-left: 22px;
    }

    .result-card li {
        margin-bottom: 6px;
    }

    .result-content {
        color: #e2e8f0;
        font-size: 16px;
        line-height: 1.7;
    }

    .project-box {
        background: #0f1929;
        border: 1px solid #1e2d45;
        border-radius: 16px;
        padding: 18px;
        margin-top: 18px;
    }

    .project-heading {
        color: #22d3ee;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .project-text {
        color: #e2e8f0;
        font-size: 18px;
        line-height: 1.8;
    }

    .stTextArea textarea,
    .stTextInput input {
        background: #0f1929 !important;
        border: 1px solid #1e2d45 !important;
        color: #e2e8f0 !important;
        border-radius: 14px !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #00d4ff, #7c3aed);
        color: white;
        border: none;
        border-radius: 14px;
        font-weight: 700;
        padding: 0.75rem 1.25rem;
    }

    div[data-testid="column"] .stButton > button {
        width: 100%;
        min-height: 64px;
        border-radius: 18px;
        font-size: 20px;
        font-weight: 700;
    }

    .footer-note {
        text-align: center;
        color: #64748b;
        font-size: 12px;
        margin-top: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------
if "active_tool" not in st.session_state:
    st.session_state.active_tool = "career"

if "career_input" not in st.session_state:
    st.session_state.career_input = ""

if "roadmap_input" not in st.session_state:
    st.session_state.roadmap_input = ""

# ---------------------------------------------------------
# Groq client
# ---------------------------------------------------------
@st.cache_resource
def get_groq_client() -> Groq:
    return Groq(api_key=GROQ_API_KEY)

def explain_project_with_groq(project_title: str, project_details: str) -> str:
    client = get_groq_client()

    prompt = f"""
You are an interview mentor.

Explain the following resume project in a short, simple, easy-to-understand 2-minute interview style.

Rules:
- Keep it short and clear
- Use simple English
- Start with what the project does
- Mention tools or technologies used
- Mention one main challenge
- Write as a single short paragraph
- Do not use headings
- Do not use bullet points
- Output only the final explanation paragraph

Project Title:
{project_title}

Project Details:
{project_details}
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=220
    )

    return response.choices[0].message.content.strip()

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def run_async(coro):
    return asyncio.run(coro)

def extract_pdf_text(uploaded_file) -> str:
    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = [page.get_text() for page in doc]
    return "\n".join(text)

def extract_projects_section(resume_text: str) -> str:
    lines = resume_text.splitlines()
    cleaned = [line.strip() for line in lines if line.strip()]

    headers = {
        "projects", "key projects", "academic projects", "personal projects", "project"
    }
    stop_headers = {
        "education", "technical skills", "skills", "experience", "certifications",
        "achievements", "internships", "declaration", "contact", "summary",
        "professional training & experience", "professional experience",
        "languages & soft skills", "languages", "soft skills"
    }

    start_idx = None
    for i, line in enumerate(cleaned):
        normalized = line.lower().strip(":")
        if normalized in headers:
            start_idx = i
            break

    if start_idx is None:
        return resume_text[:2500]

    extracted = []
    for line in cleaned[start_idx + 1:]:
        normalized = line.lower().strip(":")
        if normalized in stop_headers:
            break
        extracted.append(line)

    section_text = "\n".join(extracted).strip()
    return section_text if section_text else resume_text[:2500]

def parse_python_dict(raw_text: str):
    try:
        return ast.literal_eval(raw_text)
    except Exception:
        try:
            return json.loads(raw_text)
        except Exception:
            return {}

def parse_projects_from_result(raw_text: str) -> List[Dict[str, str]]:
    data = parse_python_dict(raw_text)
    projects = data.get("projects", [])
    return projects if isinstance(projects, list) else []

def tool_result_to_text(tool_result: Any) -> str:
    if hasattr(tool_result, "content") and isinstance(tool_result.content, list):
        parts = []
        for item in tool_result.content:
            if hasattr(item, "text"):
                parts.append(item.text)
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(tool_result)

def render_career_roles(raw_text: str):
    data = parse_python_dict(raw_text)
    roles = data.get("recommended_roles", [])

    if not roles:
        st.warning("No roles found.")
        return

    st.markdown(
        '<div class="result-card"><div class="result-title">CAREER ROLE SUGGESTIONS</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="result-content">', unsafe_allow_html=True)
    for role in roles:
        st.markdown(f"- {role}")
    st.markdown("</div></div>", unsafe_allow_html=True)

def render_roadmap(raw_text: str):
    data = parse_python_dict(raw_text)
    roadmap = data.get("roadmap", {})

    if not roadmap:
        st.warning("No roadmap found.")
        return

    st.markdown(
        '<div class="result-card"><div class="result-title">LEARNING ROADMAP</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="result-content">', unsafe_allow_html=True)
    for phase, items in roadmap.items():
        st.markdown(f"### {phase}")
        for item in items:
            st.markdown(f"- {item}")
    st.markdown("</div></div>", unsafe_allow_html=True)

def render_resume_review(raw_text: str):
    data = parse_python_dict(raw_text)
    strengths = data.get("strengths", [])
    feedback = data.get("feedback", [])

    st.markdown(
        '<div class="result-card"><div class="result-title">RESUME REVIEW</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="result-content">', unsafe_allow_html=True)

    if strengths:
        st.markdown("### Strengths")
        for item in strengths:
            st.markdown(f"- {item}")

    if feedback:
        st.markdown("### Improvements")
        for item in feedback:
            st.markdown(f"- {item}")

    st.markdown("</div></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# MCP client
# ---------------------------------------------------------
class MentorMCPClient:
    def __init__(self, server_script_path: str):
        self.server_script_path = str(Path(server_script_path).resolve())

    async def call_specific_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        if not Path(self.server_script_path).exists():
            raise FileNotFoundError(f"mcp_server.py not found at: {self.server_script_path}")

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[self.server_script_path],
            env=os.environ.copy()
        )

        async with AsyncExitStack() as exit_stack:
            stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
            read_stream, write_stream = stdio_transport

            session = await exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            await session.initialize()

            tool_result = await session.call_tool(tool_name, tool_args)
            return tool_result_to_text(tool_result)

# ---------------------------------------------------------
# UI Header
# ---------------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="hero-badge">AI Career Mentor Chatbot</div>
    <div class="hero-title">AI Career Assistant</div>
    <div class="hero-sub">
        An AI-powered chatbot for students to discover career roles, build learning roadmaps,
        review resumes, and explain projects with confidence.
    </div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("🎯 Career Roles", use_container_width=True, key="career_btn"):
        st.session_state.active_tool = "career"

with c2:
    if st.button("📘 Roadmap", use_container_width=True, key="roadmap_btn"):
        st.session_state.active_tool = "roadmap"

with c3:
    if st.button("📋 Resume Review", use_container_width=True, key="resume_btn"):
        st.session_state.active_tool = "resume"

with c4:
    if st.button("🚀 Project Explain", use_container_width=True, key="project_btn"):
        st.session_state.active_tool = "project"

server_path = Path(__file__).parent / "mcp_server.py"
mcp_client = MentorMCPClient(str(server_path))

# ---------------------------------------------------------
# Career Roles
# ---------------------------------------------------------
if st.session_state.active_tool == "career":
    with st.container():
        st.markdown('<div class="panel-title">🎯 Career Role Suggester</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Enter your skills, interests, and background.</div>', unsafe_allow_html=True)

        st.session_state.career_input = st.text_area(
            "Career input",
            value=st.session_state.career_input,
            height=180,
            placeholder="Example: I know Python, SQL, ML, DL and Gen AI. I am interested in data and AI roles.",
            label_visibility="collapsed"
        )

        if st.button("Generate Career Roles", key="generate_career_roles"):
            if not st.session_state.career_input.strip():
                st.error("Please enter your background.")
            else:
                with st.spinner("Generating career roles..."):
                    raw_tool_output = run_async(
                        mcp_client.call_specific_tool(
                            "career_role_suggester",
                            {"profile_text": st.session_state.career_input}
                        )
                    )
                render_career_roles(raw_tool_output)

# ---------------------------------------------------------
# Roadmap
# ---------------------------------------------------------
elif st.session_state.active_tool == "roadmap":
    with st.container():
        st.markdown('<div class="panel-title">📘 Skill Roadmap Generator</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Enter your target role.</div>', unsafe_allow_html=True)

        st.session_state.roadmap_input = st.text_area(
            "Roadmap input",
            value=st.session_state.roadmap_input,
            height=140,
            placeholder="Example: I want to become an AI/ML Engineer",
            label_visibility="collapsed"
        )

        if st.button("Generate Roadmap", key="generate_roadmap"):
            if not st.session_state.roadmap_input.strip():
                st.error("Please enter your target role.")
            else:
                with st.spinner("Generating roadmap..."):
                    raw_tool_output = run_async(
                        mcp_client.call_specific_tool(
                            "skill_roadmap_generator",
                            {"target_role": st.session_state.roadmap_input}
                        )
                    )
                render_roadmap(raw_tool_output)

# ---------------------------------------------------------
# Resume Review
# ---------------------------------------------------------
elif st.session_state.active_tool == "resume":
    with st.container():
        st.markdown('<div class="panel-title">📋 Resume Review</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Upload your resume PDF. The tool will extract the text and review it.</div>', unsafe_allow_html=True)

        uploaded_resume = st.file_uploader(
            "Upload Resume PDF",
            type=["pdf"],
            key="resume_pdf"
        )

        if uploaded_resume is not None:
            st.success(f"Uploaded: {uploaded_resume.name}")

        if st.button("Review Resume PDF", key="review_resume_pdf"):
            if uploaded_resume is None:
                st.error("Please upload a resume PDF.")
            else:
                with st.spinner("Reviewing resume..."):
                    resume_text = extract_pdf_text(uploaded_resume)
                    raw_tool_output = run_async(
                        mcp_client.call_specific_tool(
                            "resume_review_tool",
                            {"resume_text": resume_text}
                        )
                    )
                render_resume_review(raw_tool_output)

# ---------------------------------------------------------
# Project Explain
# ---------------------------------------------------------
elif st.session_state.active_tool == "project":
    with st.container():
        st.markdown('<div class="panel-title">🚀 Project Explanation</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="panel-sub">Upload your resume PDF. The tool will extract the projects section and generate a separate short explanation for each project.</div>',
            unsafe_allow_html=True
        )

        uploaded_project_resume = st.file_uploader(
            "Upload Resume PDF for Project Extraction",
            type=["pdf"],
            key="project_resume_pdf"
        )

        if uploaded_project_resume is not None:
            st.success(f"Uploaded: {uploaded_project_resume.name}")

        if st.button("Explain Projects From Resume", key="explain_projects_from_resume"):
            if uploaded_project_resume is None:
                st.error("Please upload a resume PDF.")
            else:
                with st.spinner("Explaining projects from resume..."):
                    resume_text = extract_pdf_text(uploaded_project_resume)
                    project_text = extract_projects_section(resume_text)

                    raw_tool_output = run_async(
                        mcp_client.call_specific_tool(
                            "project_explainer_tool",
                            {"project_details": project_text}
                        )
                    )

                    projects = parse_projects_from_result(raw_tool_output)

                if not projects:
                    st.warning("No projects found in resume.")
                else:
                    for project in projects:
                        title = project.get("title", "Project").strip()
                        details = project.get("details", "").strip()

                        explanation = explain_project_with_groq(title, details)

                        st.markdown(f"""
                        <div class="project-box">
                            <div class="project-heading">🚀 {title}</div>
                            <div class="project-text">"{explanation}"</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with st.expander("Extracted Project Section"):
                        st.text(project_text)

st.markdown('<div class="footer-note">Built with Streamlit + MCP + Groq</div>', unsafe_allow_html=True)