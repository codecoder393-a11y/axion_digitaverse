import { useState, useEffect } from "react";
import { useUser } from "../UserContext";
import { FaPaperPlane, FaWallet, FaServer } from "react-icons/fa";

type SendAcoinProps = {
  compact?: boolean;
  onSuccess?: () => Promise<void> | void;
};

function SendAcoin({ compact = false, onSuccess }: SendAcoinProps) {
  const { user } = useUser();
  const [to, setTo] = useState("");
  const [amount, setAmount] = useState("");
  const [status, setStatus] = useState("");
  const [miners, setMiners] = useState<string[]>([]);
  const [selectedMiner, setSelectedMiner] = useState("");

  useEffect(() => {
    const fetchMiners = async () => {
      try {
        const res = await fetch("http://127.0.0.1:5000/api/miners");
        if (res.ok) {
          const data = await res.json();
          setMiners(data);
          if (data.length > 0) {
            setSelectedMiner(data[0]); // Default to the first miner
          }
        }
      } catch (error) {
        console.error("Failed to fetch miners:", error);
        setStatus("Could not fetch miner list.");
      }
    };

    if (user) {
      fetchMiners();
    }
  }, [user]);

  const send = async () => {
    if (!user || !amount || !to) {
        setStatus("Please fill in all fields.");
        return;
    }
    setStatus("Sending...");
    try {
        const res = await fetch("http://127.0.0.1:5000/api/transaction", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ 
                from: user.address, 
                to, 
                amount: parseFloat(amount), 
                miner: selectedMiner 
            }),
        });
        const data = await res.json();
        if (res.ok) {
            setStatus(`Transaction successful! Block: ${data.block.index}`);
            // Clear fields after successful transaction
            setTo("");
            setAmount("");
            onSuccess?.();
        } else {
            setStatus(data.error || "Transaction failed");
        }
    } catch (error) {
        console.error("Transaction error:", error);
        setStatus("An error occurred during the transaction.");
    }
  };

  if (!user) {
    if (compact) return null;
    return (
      <div className="container py-5 text-center">
        <h2 className="fw-bold text-white"><FaPaperPlane className="me-2" />Send AXC</h2>
        <p className="fw-bold text-white">Please sign in to send AXC.</p>
      </div>
    );
  }

  const form = (
    <div className={`card shadow mx-auto p-4"`} style={{ maxWidth: 400, background: "rgba(30,40,60,0.95)" }}>
      <div className="mb-3">
        <label className="form-label fw-bold text-white">
          <FaWallet className="me-2" />To Address
        </label>
        <input 
          className="form-control fw-bold text-white bg-dark"
          value={to} 
          onChange={e => setTo(e.target.value)} 
          placeholder="Enter recipient address"
        />
      </div>
      <div className="mb-3">
        <label className="form-label fw-bold text-white">Amount (AXC)</label>
        <input 
          type="number" 
          step="0.01" 
          className="form-control fw-bold text-white bg-dark" 
          value={amount} 
          onChange={e => setAmount(e.target.value)} 
          placeholder="e.g., 0.5"
        />
      </div>
      <div className="mb-3">
          <label className="form-label fw-bold text-white">
              <FaServer className="me-2" />Miner
          </label>
          <select 
              className="form-select fw-bold text-white bg-dark" 
              value={selectedMiner} 
              onChange={e => setSelectedMiner(e.target.value)}
              disabled={miners.length === 0}
          >
              {miners.length > 0 ? (
                  miners.map(m => <option key={m} value={m}>{m.substring(0,10)}...{m.substring(m.length-10)}</option>)
              ) : (
                  <option>No miners available (default will be used)</option>
              )}
          </select>
          <div className="form-text text-light">The selected miner will process your transaction and receive the gas fee.</div>
      </div>
      <button className="btn btn-success fw-bold w-100" onClick={send}>
        <FaPaperPlane className="me-2" />Send
      </button>
      {status && <div className={`alert mt-3 ${status.startsWith("Transaction successful") ? 'alert-success' : 'alert-danger'}`}>{status}</div>}
    </div>
  );

  if (compact) return form;

  return (
    <div className="container py-5">
      <h2 className="mb-4 fw-bold text-white text-center">
        <FaPaperPlane className="me-2" /> Send AXC
      </h2>
      {form}
    </div>
  );
}

export default SendAcoin;
