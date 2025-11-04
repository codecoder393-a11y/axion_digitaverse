import { useUser } from "../UserContext";
import { useState, useEffect } from "react";
import { FaCopy, FaUser } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

import { GlassPanel, GlassButton } from './SharedUI';

function SignUpForm() {
  const { setUser } = useUser();
  const [username, setUsername] = useState("");
  const [publicKey, setPublicKey] = useState("");
  const [privateKey, setPrivateKey] = useState("");
  const [showKeys, setShowKeys] = useState(false);
  const [counter, setCounter] = useState(15);
  const navigate = useNavigate();

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (showKeys && counter > 0) {
      timer = setTimeout(() => setCounter(counter - 1), 1000);
    }
    if (showKeys && counter === 0) {
      navigate("/");
    }
    return () => clearTimeout(timer);
  }, [showKeys, counter, navigate]);

  const handleSignUp = async (e: any) => {
    e.preventDefault();
    const res = await fetch("http://127.0.0.1:5001/api/create-user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username }),
    });
    const data = await res.json();
    setPublicKey(data.publicKey);
    setPrivateKey(data.privateKey);
    setShowKeys(true);
    setUser({ username, address: data.publicKey, token: data.privateKey });
  };

  const copyToClipboard = (text: string) => navigator.clipboard.writeText(text);

  return (
    <div className="container py-5">
      <form onSubmit={handleSignUp} style={{ maxWidth: 400 }} className="mx-auto">
        <GlassPanel className="p-4">
          <h2 className="fw-bold text-white text-center">
            <FaUser className="me-2 text-white" /> Sign Up
          </h2>
          <input
            className="form-control mb-3 fw-bold text-white"
            placeholder="Username"
            value={username}
            onChange={e => setUsername(e.target.value)}
            required
          />
          <GlassButton type="submit" className="w-100 fw-bold" variant="primary">Sign Up</GlassButton>
          {showKeys && (
            <div className="mt-4">
              <div className="fw-bold text-white">Public Key: {publicKey}
                <button className="btn btn-outline-secondary btn-sm ms-2" onClick={() => copyToClipboard(publicKey)}>
                  <FaCopy /> Copy
                </button>
              </div>
              <div className="fw-bold text-danger mt-2">Private Key: {privateKey}
                <button className="btn btn-outline-secondary btn-sm ms-2" onClick={() => copyToClipboard(privateKey)}>
                  <FaCopy /> Copy
                </button>
              </div>
              <div className="text-warning mt-1" style={{ fontSize: 12 }}>
                Never share your private key. Keep it safe!
              </div>
              <div className="mt-3 fw-bold text-info text-center">
                Redirecting to home in {counter} seconds...
              </div>
            </div>
          )}
        </GlassPanel>
      </form>
    </div>
  );
}

export default SignUpForm;