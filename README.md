# 📝 Meeting Summary App

A full-stack web application that transcribes meeting notes, summarizes them using **Groq LLMs**, and allows you to **share the summary via email**.  
Deployed on **Render**: [summary-7.onrender.com](https://summary-7.onrender.com)

---

## 🚀 Features
- **Frontend (React)**  
  - User interface to paste or upload transcripts.  
  - Sends transcript + custom prompt to backend.  
  - Displays summarized text.  
  - Allows sharing summary via email.  

- **Backend (Flask)**  
  - Exposes REST API endpoints:
    - `POST /summarize` → Summarizes transcript with Groq LLM.  
    - `POST /share` → Sends summary via email using SendGrid.  
    - `GET /health` → Health check endpoint.  
  - Hosts built React frontend (served from `frontend/build`).  
  - Handles proxy issues on Render.  

- **LLM Integration (Groq)**  
  - Uses the `groq` Python SDK.  
  - Model: `llama-3.3-70b-versatile`.  

- **Email Sharing (SendGrid)**  
  - Sends generated summary to multiple recipients.  

---
