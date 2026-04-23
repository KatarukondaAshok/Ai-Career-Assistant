from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CareerPilot AI MCP Server")


def unique_keep_order(items: List[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        key = item.strip().lower()
        if key and key not in seen:
            seen.add(key)
            result.append(item)
    return result


@mcp.tool()
def career_role_suggester(profile_text: str) -> Dict[str, Any]:
    if not profile_text or not profile_text.strip():
        return {"error": "Profile text is empty."}

    profile = profile_text.lower()
    roles = []

    if "python" in profile:
        roles.extend(["Python Developer", "Data Analyst", "AI/ML Engineer"])
    if "sql" in profile:
        roles.extend(["Data Analyst", "BI Analyst", "Database Developer"])
    if "ml" in profile or "machine learning" in profile:
        roles.extend(["Machine Learning Engineer", "AI Engineer", "Data Scientist"])
    if "dl" in profile or "deep learning" in profile:
        roles.extend(["Deep Learning Engineer", "Computer Vision Engineer", "NLP Engineer"])
    if "gen ai" in profile or "generative ai" in profile or "llm" in profile:
        roles.extend(["Generative AI Engineer", "LLM Engineer", "AI Solutions Engineer"])
    if "power bi" in profile or "tableau" in profile:
        roles.extend(["Data Analyst", "BI Analyst", "Reporting Analyst"])
    if "react" in profile or "frontend" in profile:
        roles.extend(["Frontend Developer", "UI Developer"])
    if "node" in profile or "backend" in profile:
        roles.extend(["Backend Developer", "Full Stack Developer"])

    if not roles:
        roles = ["Software Engineer", "Data Analyst", "Trainee AI/ML Engineer"]

    return {
        "recommended_roles": unique_keep_order(roles)[:8]
    }


@mcp.tool()
def skill_roadmap_generator(target_role: str) -> Dict[str, Any]:
    if not target_role or not target_role.strip():
        return {"error": "Target role is empty."}

    role = target_role.lower()

    if "data analyst" in role:
        roadmap = {
            "Phase 1": ["Learn Python basics", "Learn SQL", "Understand Excel"],
            "Phase 2": ["Practice pandas and NumPy", "Learn statistics", "Do EDA"],
            "Phase 3": ["Learn Power BI or Tableau", "Build dashboards"],
            "Phase 4": ["Build projects", "Prepare resume", "Practice interviews"]
        }
    elif "ai" in role or "ml" in role or "machine learning" in role:
        roadmap = {
            "Phase 1": ["Learn Python", "Learn statistics", "Understand ML basics"],
            "Phase 2": ["Learn scikit-learn", "Practice regression and classification"],
            "Phase 3": ["Learn deep learning", "Build ML projects", "Learn deployment"],
            "Phase 4": ["Prepare resume", "Explain projects", "Practice interviews"]
        }
    elif "full stack" in role:
        roadmap = {
            "Phase 1": ["Learn HTML, CSS, JavaScript", "Learn Git and GitHub"],
            "Phase 2": ["Learn React", "Build frontend projects"],
            "Phase 3": ["Learn backend development", "Learn databases"],
            "Phase 4": ["Build full-stack projects", "Deploy and prepare interviews"]
        }
    else:
        roadmap = {
            "Phase 1": ["Learn fundamentals"],
            "Phase 2": ["Build projects"],
            "Phase 3": ["Create portfolio"],
            "Phase 4": ["Prepare interviews"]
        }

    return {"roadmap": roadmap}


@mcp.tool()
def resume_review_tool(resume_text: str) -> Dict[str, Any]:
    if not resume_text or not resume_text.strip():
        return {"error": "Resume text is empty."}

    text = resume_text.lower()
    strengths = []
    feedback = []

    if "python" in text:
        strengths.append("Python is included.")
    if "sql" in text:
        strengths.append("SQL is included.")
    if "project" in text:
        strengths.append("Projects section is present.")
    if "github" in text:
        strengths.append("GitHub link is included.")
    if "linkedin" in text:
        strengths.append("LinkedIn link is included.")

    if "linkedin" not in text:
        feedback.append("Add LinkedIn profile link.")
    if "github" not in text:
        feedback.append("Add GitHub profile link.")
    if "project" not in text:
        feedback.append("Add a projects section.")
    if len(resume_text.split()) < 150:
        feedback.append("Add more project details and measurable impact.")

    if not feedback:
        feedback.append("Resume looks good. Improve bullet points with quantified achievements.")

    return {
        "strengths": strengths,
        "feedback": feedback
    }


def split_projects_generic(project_details: str) -> List[Dict[str, str]]:
    """
    Generic splitter for resume project sections.
    Best when projects look like:
    Project Name | Tools
    followed by bullet points/details.
    """
    lines = [line.strip() for line in project_details.splitlines() if line.strip()]
    projects: List[Dict[str, str]] = []

    current_title = None
    current_details: List[str] = []

    for line in lines:
        if "|" in line and not line.startswith("•"):
            if current_title:
                projects.append({
                    "title": current_title,
                    "details": "\n".join(current_details).strip()
                })
            current_title = line
            current_details = []
        else:
            if current_title is None:
                current_title = "Project"
            current_details.append(line)

    if current_title:
        projects.append({
            "title": current_title,
            "details": "\n".join(current_details).strip()
        })

    cleaned_projects = []
    for p in projects:
        title = p.get("title", "").strip()
        details = p.get("details", "").strip()
        if title or details:
            cleaned_projects.append({
                "title": title if title else "Project",
                "details": details
            })

    if not cleaned_projects:
        cleaned_projects.append({
            "title": "Project",
            "details": project_details
        })

    return cleaned_projects


@mcp.tool()
def project_explainer_tool(project_details: str) -> Dict[str, Any]:
    if not project_details or not project_details.strip():
        return {"error": "Project details are empty."}

    projects = split_projects_generic(project_details)
    return {"projects": projects}


if __name__ == "__main__":
    mcp.run(transport="stdio")