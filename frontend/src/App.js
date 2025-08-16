import { useState } from "react";

function App() {
  const [text, setText] = useState("");
  const [summary, setSummary] = useState("");
  const [emails, setEmails] = useState("");
  const [message, setMessage] = useState("");
  const [sendResults, setSendResults] = useState([]);

  const handleSummarize = async (e) => {
    e.preventDefault();
    setMessage("");
    setSendResults([]);

    try {
      const response = await fetch("http://127.0.0.1:5000/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript: text, prompt: "Summarize in bullet points" }),
      });

      const data = await response.json();
      if (data.summary) setSummary(data.summary);
      else if (data.error) setMessage(data.error);
    } catch (err) {
      setMessage("Error connecting to backend");
      console.error(err);
    }
  };

  const handleShare = async () => {
    setMessage("");
    setSendResults([]);
    const recipientList = emails.split(",").map(e => e.trim()).filter(e => e);

    if (!summary || recipientList.length === 0) {
      setMessage("Please provide summary and recipient emails.");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:5000/share", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ summary, recipients: recipientList }),
      });

      const data = await response.json();
      if (data.status === "success") {
        setMessage("Summary shared successfully!");
        setSendResults(data.results);
      } else {
        setMessage(data.error || "Failed to share summary");
        setSendResults(recipientList.map(email => ({ email, status: "Failed" })));
      }
    } catch (err) {
      setMessage("Error connecting to backend");
      console.error(err);
      setSendResults(recipientList.map(email => ({ email, status: "Failed" })));
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "700px", margin: "auto" }}>
      <h2>AI Meeting Notes Summarizer</h2>
      <form onSubmit={handleSummarize}>
        <textarea
          rows="10"
          style={{ width: "100%" }}
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder="Paste your meeting notes here..."
        />
        <button type="submit" style={{ marginTop: "10px" }}>Summarize</button>
      </form>

      {summary && (
        <div style={{ marginTop: "20px" }}>
          <h3>Summary (editable):</h3>
          <textarea
            rows="8"
            style={{ width: "100%" }}
            value={summary}
            onChange={e => setSummary(e.target.value)}
          />
          <div style={{ marginTop: "10px" }}>
            <input
              type="text"
              style={{ width: "100%" }}
              value={emails}
              onChange={e => setEmails(e.target.value)}
              placeholder="Enter recipient emails, separated by commas"
            />
            <button onClick={handleShare} style={{ marginTop: "10px" }}>Share Summary</button>
          </div>
        </div>
      )}

      {message && <p style={{ marginTop: "10px", color: "red" }}>{message}</p>}

      {sendResults.length > 0 && (
        <div style={{ marginTop: "10px" }}>
          <h4>Send Results:</h4>
          <ul>
            {sendResults.map((res, idx) => (
              <li key={idx}>
                {res.email}: {res.status} {res.error ? `(${res.error})` : ""}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
