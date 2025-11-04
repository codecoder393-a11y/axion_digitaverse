import { useState } from "react";
import { FaUserSecret, FaMoneyBillWave } from "react-icons/fa";

const AGENTS = [
  { name: "Agent Alice", address: "agent_pubkey_1", location: "Downtown" },
  { name: "Agent Bob", address: "agent_pubkey_2", location: "Mall" },
];

function Agents() {
  const [selectedAgent, setSelectedAgent] = useState<any>(null);
  const [amount, setAmount] = useState("");
  const [status, setStatus] = useState("");

  const handleDeposit = async () => {
    setStatus("Processing...");
    // Simulate deposit (in real app, call backend to transfer acoin from agent to user)
    setTimeout(() => {
      setStatus(`Deposited ${amount} acoin from ${selectedAgent.name}`);
      setAmount("");
      setSelectedAgent(null);
    }, 1200);
  };

  return (
    <div className="container py-5">
      <h2 className="mb-4 text-center text-white">
        <FaUserSecret className="me-2" /> Axion Agents
      </h2>
      <div className="row">
        {AGENTS.map(agent => (
          <div className="col-md-6 mb-4" key={agent.address}>
            <div className="card shadow">
              <div className="card-body">
                <h5 className="card-title">{agent.name}</h5>
                <p>
                  <strong>Location:</strong> {agent.location}<br />
                  <strong>Address:</strong> {agent.address}
                </p>
                <button className="btn btn-success" onClick={() => setSelectedAgent(agent)}>
                  <FaMoneyBillWave className="me-2" /> Buy acoin from Agent
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
      {selectedAgent && (
        <div className="card shadow p-4 mx-auto" style={{ maxWidth: 400 }}>
          <h5>Deposit from {selectedAgent.name}</h5>
          <input
            type="number"
            className="form-control mb-2"
            placeholder="Amount of acoin"
            value={amount}
            onChange={e => setAmount(e.target.value)}
          />
          <button className="btn btn-primary w-100" onClick={handleDeposit}>
            Deposit
          </button>
          {status && <div className="alert alert-info mt-2">{status}</div>}
        </div>
      )}
    </div>
  );
}

export default Agents;