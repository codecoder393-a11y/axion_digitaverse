import { useState } from "react";
import { useNavigate } from "react-router-dom";

function AxionAI() {
  const [prompt, setPrompt] = useState("");
  const [reply, setReply] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const askAI = async () => {
    setLoading(true);
    setReply("");
    const res = await fetch("https://axion-digitaverse-3.onrender.com/api/axion-ai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    const data = await res.json();
    setReply(data.reply || data.error || "No response");
    setLoading(false);
  };

  return (
    <div className="container py-4">
      <h2 className="fw-bold mb-3">Axion AI Blockchain Assistant</h2>
      <textarea
        className="form-control mb-2"
        rows={3}
        placeholder="Ask Axion AI about blockchain, smart contracts, code, etc..."
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
      />
      <button className="btn btn-primary fw-bold mb-3" onClick={askAI} disabled={loading || !prompt}>
        {loading ? "Thinking..." : "Ask Axion AI"}
      </button>
      <button className="btn btn-outline-info mb-3 ms-2" onClick={() => navigate("/axion-ai-dashboard")}>
        View AI Dashboard
      </button>
      {reply && (
        <div className="alert alert-info" style={{ whiteSpace: "pre-wrap" }}>
          <b>Axion AI:</b> {reply}
        </div>
      )}
    </div>
  );
}

export default AxionAI;