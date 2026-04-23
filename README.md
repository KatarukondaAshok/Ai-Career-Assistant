#  AI Career Assistant  
### LLM + MCP Powered Mentor Chatbot for B.Tech Graduates  


##  Live Application

You can access the deployed application here:

 https://huggingface.co/spaces/katarukondaashok143/chatbot_using_mcp
 
---

##  Overview

AI Career Assistant is an intelligent mentor chatbot designed to guide B.Tech graduates in their career journey using **Large Language Models (LLMs)** and **Model Context Protocol (MCP)**.

It provides:
- Personalized career recommendations  
- Skill roadmaps  
- Resume feedback  
- Project explanations  

All through an interactive **Streamlit interface**.

---

##  Problem Statement

Many students struggle with:

- Choosing the right career path  
- Understanding required skills for specific roles  
- Improving resumes for ATS systems  
- Explaining projects confidently in interviews  

This project solves these challenges by delivering **structured, real-time AI guidance**.

---

##  Key Features

###  Career Role Suggestions  
Suggests job roles based on skills, interests, and degree  

###  Skill Roadmap Generator  
Provides step-by-step learning path  

###  Resume Review Tool  
Analyzes resume and gives improvement suggestions  

###  Project Explainer  
Converts projects into interview-ready explanations  

---

##  Architecture

User (Streamlit UI)
↓
LLM (Grok API / Gemini)
↓
Tool Selection (Prompt-based)
↓
MCP Server (Tool Execution)
↓
Response → UI


---

##  MCP Tools Used

| Tool Name | Purpose |
|----------|--------|
| career_role_suggester | Suggests suitable job roles |
| skill_roadmap_generator | Generates learning roadmap |
| resume_review_tool | Reviews and improves resume |
| project_explainer_tool | Converts project into interview explanation |

---

##  Tech Stack

- **Frontend**: Streamlit  
- **Backend**: Python  
- **LLM Integration**: Grok API / Gemini  
- **Protocol**: MCP (Model Context Protocol)  
- **Communication**: JSON-RPC  
- **Deployment**: Hugging Face Spaces  

---

##  Project Structure


project/
│
├── app.py
├── mcp_server.py
├── requirements.txt
├── .env
└── README.md


---

##  How It Works

1. User enters query (career / resume / project)  
2. LLM analyzes intent  
3. Selects appropriate MCP tool  
4. Sends request to MCP server  
5. Tool processes input  
6. Response returned to UI  

---

##  Installation & Setup

### 1️⃣ Clone Repository
```bash
git clone https://github.com/your-username/ai-career-assistant.git
cd ai-career-assistant
2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Add API Key

Create .env file:

XAI_API_KEY=your_grok_api_key
5️⃣ Run Application
streamlit run app.py
🌐 Deployment
Hugging Face Spaces
Streamlit Cloud
Docker (optional)


Future Improvements
Voice-based interaction
Real-time job listings
Multi-language support
ATS score integration
RAG-based knowledge system

 Use Cases
Students preparing for placements
Fresh graduates exploring careers
Resume optimization
Interview preparation

 Example Inputs
"Suggest career roles for Python + ML student"
"Generate roadmap for Data Scientist"
"Review my resume"
"Explain my ML project for interview"

 Contribution

Contributions are welcome!
Feel free to fork and submit a PR.
