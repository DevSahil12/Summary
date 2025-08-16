import os
from groq import Groq

_client = None

def get_client():
    global _client
    if _client is None:
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY is not set")
        _client = Groq(api_key=key)
    return _client

def summarize(transcript: str, instruction: str) -> str:
    client = get_client()
    # Short, deterministic summaries; increase max_tokens if you want longer
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=900,
        messages=[
            {"role": "system",
             "content": "You summarize meeting transcripts into clean, structured outputs. "
                        "Follow the user's instruction. Prefer bullet points, headings, and action items."},
            {"role": "user",
             "content": f"Instruction:\n{instruction}\n\nTranscript:\n{transcript}"}
        ],
    )
    return resp.choices[0].message.content or ""
