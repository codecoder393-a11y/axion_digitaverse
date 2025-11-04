import { useEffect, useState } from "react";
import { useUser } from "../UserContext";
import CreateLoan from "./CreateLoan";
import { motion } from "framer-motion";

// Helper function to shorten addresses
function shortAddress(address: string) {
  if (!address) return "";
  return address.slice(0, 8) + "..." + address.slice(-4);
}

function LenderDashboard() {
  const { user } = useUser();
  const [loans, setLoans] = useState<any[]>([]);
  const [requests, setRequests] = useState<any[]>([]);
  const [approved, setApproved] = useState<number | null>(null);

  const fetchChain = async () => {
    const res = await fetch("http://127.0.0.1:5001/api/chain");
    const data = await res.json();
    const myLoans = data.filter((block: any) => block.data.type === "loan" && block.data.lender === user?.address);
    setLoans(myLoans);
    const myLoanIds = myLoans.map((b: any) => b.data.loan_id);
    const reqs = data.filter(
      (block: any) =>
        block.data.type === "loan_request" && myLoanIds.includes(block.data.loan_id)
    );
    setRequests(reqs);
  };

  useEffect(() => {
    fetchChain();
    // eslint-disable-next-line
  }, []);

  const handleApprove = async (loanId: number) => {
    await fetch("http://127.0.0.1:5001/api/approve-loan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ loan_id: loanId, lender: user?.address })
    });
    setApproved(loanId);
    setTimeout(() => setApproved(null), 2000);
    fetchChain();
  };

  return (
    <div className="container py-5">
      <h2 className="mb-4 text-center text-white fw-bold" style={{ letterSpacing: 2 }}>Lender Dashboard</h2>
      <CreateLoan onLoanCreated={fetchChain} />
      <div className="row">
        {loans.map((block: any, idx: number) => (
          <motion.div
            className="col-md-6 mb-4"
            key={block.data.loan_id}
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: idx * 0.1 }}
          >
            <div className="card shadow">
              <div className="card-body">
                <h5 className="card-title">Loan #{block.data.loan_id}</h5>
                <p className="card-text">
                  <strong>Amount:</strong> ${block.data.amount}<br />
                  <strong>Rate:</strong> {block.data.rate}%<br />
                  <strong>Duration:</strong> {block.data.duration} months
                </p>
                <h6>Requests:</h6>
                {requests
                  .filter((req: any) => req.data.loan_id === block.data.loan_id)
                  .map((req: any, idx: number) => (
                    <motion.div
                      key={idx}
                      className="mb-2"
                      initial={{ opacity: 0, x: 40 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.4, delay: idx * 0.1 }}
                    >
                      <strong>Borrower:</strong> {shortAddress(req.data.borrower)}<br />
                      <strong>Method:</strong> {req.data.method}<br />
                      <button
                        className="btn btn-success btn-sm mt-1"
                        onClick={() => handleApprove(block.data.loan_id)}
                        disabled={approved === block.data.loan_id}
                      >
                        {approved === block.data.loan_id ? "Approved!" : "Approve & Send"}
                      </button>
                    </motion.div>
                  ))}
                {requests.filter((req: any) => req.data.loan_id === block.data.loan_id).length === 0 && (
                  <p>No requests yet.</p>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

export default LenderDashboard;