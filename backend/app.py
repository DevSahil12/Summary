from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from groq import Groq
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import traceback

# ---------------------------------------
# Fix Render proxy issue (remove env vars)
# ---------------------------------------
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

# Point Flask to React build folder
app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
CORS(app)  # allow requests from frontend

# -------------------------------
# Serve React frontend
# -------------------------------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


# -------------------------------
# Initialize Groq client
# -------------------------------
_client = None
def get_client():
    global _client
    if _client is None:
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY is not set")
        # ✅ Fixed: removed `proxies` argument
        _client = Groq(api_key=key)
    return _client


# -------------------------------
# Summarize function
# -------------------------------
def summarize(transcript, prompt):
    client = get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",   # ✅ new supported model
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": transcript},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()



# -------------------------------
# API Routes
# -------------------------------
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
        print("🔥 Error in /summarize:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health_check():
    return "Backend is running!"


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
                from_email="sharmas80928@gmail.com",
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


# -------------------------------
# Run app
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
