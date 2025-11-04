import { useState } from "react";
import { FaUserSecret, FaCopy } from "react-icons/fa";

function RegisterAgent() {
  const [username, setUsername] = useState("");
  const [publicKey, setPublicKey] = useState("");
  const [privateKey, setPrivateKey] = useState("");
  const [status, setStatus] = useState("");

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Registering...");
    const res = await fetch("http://127.0.0.1:5001/api/register-agent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username }),
    });
    const data = await res.json();
    setPublicKey(data.publicKey);
    setPrivateKey(data.privateKey);
    setStatus(data.message);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="container py-5">
      <h2 className="mb-4 text-center text-white"><FaUserSecret className="me-2" /> Register as Agent</h2>
      <form className="card shadow mx-auto p-4" style={{ maxWidth: 400 }} onSubmit={handleRegister}>
        <div className="mb-3">
          <label className="form-label">Agent Username</label>
          <input type="text" className="form-control" value={username} onChange={e => setUsername(e.target.value)} required />
        </div>
        <button className="btn btn-primary w-100" type="submit">Register</button>
        {status && <div className="alert alert-info mt-3">{status}</div>}
        {publicKey && (
          <div className="mt-3">
            <strong>Public Key:</strong> <span>{publicKey}</span>
            <button className="btn btn-outline-secondary btn-sm ms-2" onClick={() => copyToClipboard(publicKey)}>
              <FaCopy /> Copy
            </button>
          </div>
        )}
        {privateKey && (
          <div className="mt-2">
            <strong>Private Key:</strong> <span className="text-danger">{privateKey}</span>
            <button className="btn btn-outline-secondary btn-sm ms-2" onClick={() => copyToClipboard(privateKey)}>
              <FaCopy /> Copy
            </button>
            <div className="text-warning mt-1" style={{ fontSize: 12 }}>
              Never share your private key. Keep it safe!
            </div>
          </div>
        )}
      </form>
    </div>
  );
}

export default RegisterAgent;