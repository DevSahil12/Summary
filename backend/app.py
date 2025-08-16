from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from groq import Groq
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)
CORS(app)  # allow requests from frontend

# Initialize Groq client
_client = None
def get_client():
    global _client
    if _client is None:
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY is not set")
        _client = Groq(api_key=key)
    return _client

# Summarize function
def summarize(transcript: str, instruction: str) -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=900,
        messages=[
            {"role": "system",
             "content": "You summarize meeting transcripts into clean, structured outputs. Prefer bullet points, headings, and action items."},
            {"role": "user",
             "content": f"Instruction:\n{instruction}\n\nTranscript:\n{transcript}"}
        ],
    )
    return resp.choices[0].message.content or ""

# Health check
@app.route("/")
def home():
    return "Backend is running!"

# Summarize endpoint
@app.route("/summarize", methods=["POST"])
def summarize_route():
    data = request.json
    transcript = data.get("transcript")
    prompt = data.get("prompt", "Summarize in bullet points")
    if not transcript:
        return jsonify({"error": "Transcript is required"}), 400

    try:
        summary = summarize(transcript, prompt)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Share endpoint (SendGrid)
@app.route("/share", methods=["POST"])
def share():
    data = request.json
    summary = data.get("summary")
    recipients = data.get("recipients", [])

    if not summary or not recipients:
        return jsonify({"error": "Summary and recipients are required"}), 400

    sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")
    if not sendgrid_api_key:
        return jsonify({"error": "SendGrid API key not set"}), 500

    results = []
    for email in recipients:
        try:
            message = Mail(
                from_email="sharmas80928@gmail.com",  # verified Gmail sender
                to_emails=email,
                subject="Meeting Summary",
                plain_text_content=summary
            )
            sg = SendGridAPIClient(sendgrid_api_key)
            response = sg.send(message)
            results.append({"email": email, "status": "Sent", "code": response.status_code})
        except Exception as e:
            results.append({"email": email, "status": "Failed", "error": str(e)})

    return jsonify({"status": "success", "results": results})

if __name__ == "__main__":
    app.run(debug=True)
