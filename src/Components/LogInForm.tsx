import { useUser } from "../UserContext";
import { useState } from "react";
import { FaUser } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import { fetchApi, API_ENDPOINTS } from "../utils/api";

import { GlassPanel, GlassButton } from './SharedUI';

function LoginForm() {
  const { setUser } = useUser();
  const [publicKey, setPublicKey] = useState("");
  const [privateKey, setPrivateKey] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e: any) => {
    e.preventDefault();
    try {
      console.log('Making login request to:', import.meta.env.VITE_API_URL + API_ENDPOINTS.LOGIN);
      const res = await fetchApi(API_ENDPOINTS.LOGIN, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ publicKey, privateKey }),
      });
      console.log('Login response:', res);
      const data = await res.json();
      console.log('Login data:', data);
      
      if (res.ok) {
        setUser(data.user); // <-- includes balance
        navigate("/welcome");
      } else {
        setError(data.message || "Login failed");
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err instanceof Error ? err.message : 'Login failed');
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