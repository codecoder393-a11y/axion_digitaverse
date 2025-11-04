import { useState } from "react";
import { useUser } from "../UserContext";

function CreateLoan({ onLoanCreated }: { onLoanCreated: () => void }) {
  const { user } = useUser();
  const [amount, setAmount] = useState("");
  const [rate, setRate] = useState("");
  const [duration, setDuration] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const res = await fetch("http://127.0.0.1:5001/api/create-loan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        lender: user?.address,
        amount,
        rate,
        duration
      })
    });
    setLoading(false);
    if (res.ok) {
      setAmount("");
      setRate("");
      setDuration("");
      onLoanCreated();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <h4>Create a Loan Offer</h4>
      <div className="mb-2">
        <input type="number" className="form-control" placeholder="Amount" value={amount} onChange={e => setAmount(e.target.value)} required />
      </div>
      <div className="mb-2">
        <input type="text" className="form-control" placeholder="Interest Rate (%)" value={rate} onChange={e => setRate(e.target.value)} required />
      </div>
      <div className="mb-2">
        <input type="text" className="form-control" placeholder="Duration (months)" value={duration} onChange={e => setDuration(e.target.value)} required />
      </div>
      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? "Creating..." : "Create Loan"}
      </button>
    </form>
  );
}

export default CreateLoan;