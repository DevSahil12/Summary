import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

chat_completion = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "Hello! Can you summarize yourself in one sentence?"}
    ],
    model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)

