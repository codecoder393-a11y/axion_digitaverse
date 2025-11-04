import { useState } from "react";
import { FaMoneyBillWave } from "react-icons/fa";

function AgentDeposit() {
  const [agentAddress, setAgentAddress] = useState("");
  const [userAddress, setUserAddress] = useState("");
  const [amount, setAmount] = useState("");
  const [status, setStatus] = useState("");

  const handleDeposit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Processing...");
    const res = await fetch("http://127.0.0.1:5001/api/agent-deposit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agent_address: agentAddress, user_address: userAddress, amount }),
    });
    const data = await res.json();
    setStatus(data.message || data.error);
  };

  return (
    <div className="container py-5">
      <h2 className="mb-4 text-center text-white"><FaMoneyBillWave className="me-2" /> Agent Deposit</h2>
      <form className="card shadow mx-auto p-4" style={{ maxWidth: 400 }} onSubmit={handleDeposit}>
        <div className="mb-3">
          <label className="form-label">Agent Address</label>
          <input type="text" className="form-control" value={agentAddress} onChange={e => setAgentAddress(e.target.value)} required />
        </div>
        <div className="mb-3">
          <label className="form-label">User Address</label>
          <input type="text" className="form-control" value={userAddress} onChange={e => setUserAddress(e.target.value)} required />
        </div>
        <div className="mb-3">
          <label className="form-label">Amount (acoin)</label>
          <input type="number" className="form-control" value={amount} onChange={e => setAmount(e.target.value)} required />
        </div>
        <button className="btn btn-success w-100" type="submit">Deposit</button>
        {status && <div className="alert alert-info mt-3">{status}</div>}
      </form>
    </div>
  );
}

export default AgentDeposit;