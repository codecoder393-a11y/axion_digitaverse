import { useState } from "react";
import { useUser } from "../UserContext";
import { motion } from "framer-motion";

function TransactionForm() {
  const { user } = useUser();
  const [to, setTo] = useState("");
  const [amount, setAmount] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus("");
    const res = await fetch("http://127.0.0.1:5001/api/transaction", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        from: user?.address,
        to,
        amount,
        miner: user?.address // For demo, sender is also miner
      })
    });
    setLoading(false);
    if (res.ok) {
      setStatus("Transaction successful!");
      setTo("");
      setAmount("");
    } else {
      const data = await res.json();
      setStatus(data.error || "Transaction failed");
    }
  };

  return (
    <div className="container py-5">
      <motion.div
        className="card shadow mx-auto p-4"
        style={{ maxWidth: 400 }}
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="mb-4 text-center text-white">Send acoin</h2>
        <form onSubmit={handleSend}>
          <div className="mb-3">
            <label className="form-label">Recipient Address</label>
            <input type="text" className="form-control" value={to} onChange={e => setTo(e.target.value)} required />
          </div>
          <div className="mb-3">
            <label className="form-label">Amount</label>
            <input type="number" className="form-control" value={amount} onChange={e => setAmount(e.target.value)} required />
          </div>
          <button className="btn btn-primary w-100" type="submit" disabled={loading}>
            {loading ? "Sending..." : "Send"}
          </button>
          {status && <div className="alert alert-info mt-3">{status}</div>}
        </form>
      </motion.div>
    </div>
  );
}

export default TransactionForm;