import { useUser } from "../UserContext";
import { useState } from "react";
import { FaUser } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

import { GlassPanel, GlassButton } from './SharedUI';

function LoginForm() {
  const { setUser } = useUser();
  const [publicKey, setPublicKey] = useState("");
  const [privateKey, setPrivateKey] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e: any) => {
    e.preventDefault();
    const res = await fetch("http://127.0.0.1:5000/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ publicKey, privateKey }),
    });
    const data = await res.json();
    if (res.ok) {
      setUser(data.user); // <-- includes balance
      navigate("/wallet");
    } else {
      setError(data.message || "Login failed");
    }
  };

  return (
    <div className="container py-5">
      <form onSubmit={handleLogin} style={{ maxWidth: 400 }} className="mx-auto">
        <GlassPanel className="p-4">
          <h2 className="fw-bold text-white text-center">
            <FaUser className="me-2 text-white" /> Login
          </h2>
          <input
            className="form-control mb-3 fw-bold text-white"
            placeholder="Public Key"
            value={publicKey}
            onChange={e => setPublicKey(e.target.value)}
            required
          />
          <input
            className="form-control mb-3 fw-bold text-white"
            placeholder="Private Key"
            value={privateKey}
            onChange={e => setPrivateKey(e.target.value)}
            required
          />
          <GlassButton type="submit" className="w-100 fw-bold" variant="primary">Login</GlassButton>
          {error && <div className="alert alert-danger mt-2 fw-bold">{error}</div>}
        </GlassPanel>
      </form>
    </div>
  );
}

export default LoginForm;