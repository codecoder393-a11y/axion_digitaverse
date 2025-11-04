import { useEffect, useState } from "react";
import { useUser } from "../UserContext";
import { motion } from "framer-motion";

function BorrowerDashboard() {
  const { user } = useUser();
  const [loans, setLoans] = useState<any[]>([]);
  const [requests, setRequests] = useState<any[]>([]);
  const [approvals, setApprovals] = useState<any[]>([]);
  const [method, setMethod] = useState("");
  const [requested, setRequested] = useState<number | null>(null);

  useEffect(() => {
    const fetchChain = async () => {
      const res = await fetch("http://127.0.0.1:5001/api/chain");
      const data = await res.json();
      setLoans(data.filter((block: any) => block.data.type === "loan"));
      setRequests(data.filter((block: any) => block.data.type === "loan_request" && block.data.borrower === user?.address));
      setApprovals(data.filter((block: any) => block.data.type === "loan_approval"));
    };
    fetchChain();
    // eslint-disable-next-line
  }, [user]);

  const handleRequest = async (loanId: number) => {
    await fetch("http://127.0.0.1:5001/api/request-loan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        loan_id: loanId,
        borrower: user?.address,
        method
      })
    });
    setRequested(loanId);
    setTimeout(() => setRequested(null), 2000);
    // Refresh requests and approvals
    const res = await fetch("http://127.0.0.1:5001/api/chain");
    const data = await res.json();
    setRequests(data.filter((block: any) => block.data.type === "loan_request" && block.data.borrower === user?.address));
    setApprovals(data.filter((block: any) => block.data.type === "loan_approval"));
  };

  const isApproved = (loan_id: number) =>
    approvals.some((a: any) => a.data.loan_id === loan_id);

  return (
    <div className="bg-primary-subtle">
      <div className="container py-5">
        <h2 className="mb-4 text-center text-white fw-bold" style={{ letterSpacing: 2 }}>Borrower Dashboard</h2>
        <h4 className="text-white">Available Loans</h4>
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
                    <strong>Lender:</strong> {block.data.lender}<br />
                    <strong>Amount:</strong> ${block.data.amount}<br />
                    <strong>Rate:</strong> {block.data.rate}%<br />
                    <strong>Duration:</strong> {block.data.duration} months
                  </p>
                  <input
                    type="text"
                    className="form-control mb-2"
                    placeholder="Payment Method (e.g. Bank, Crypto)"
                    value={method}
                    onChange={e => setMethod(e.target.value)}
                  />
                  <button
                    className="btn btn-success"
                    onClick={() => handleRequest(block.data.loan_id)}
                    disabled={requested === block.data.loan_id || requests.some((r: any) => r.data.loan_id === block.data.loan_id)}
                  >
                    {requested === block.data.loan_id
                      ? "Requested!"
                      : requests.some((r: any) => r.data.loan_id === block.data.loan_id)
                      ? "Already Requested"
                      : "Request Loan"}
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
        <h4 className="mt-5 text-white">Your Loan Requests</h4>
        <div className="row">
          {requests.length === 0 && <div className="text-muted">No requests yet.</div>}
          {requests.map((req: any, idx: number) => (
            <motion.div
              className="col-md-6 mb-4"
              key={req.data.loan_id}
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: idx * 0.1 }}
            >
              <div className="card shadow">
                <div className="card-body">
                  <h5 className="card-title">Loan #{req.data.loan_id}</h5>
                  <p className="card-text">
                    <strong>Method:</strong> {req.data.method}<br />
                    <strong>Status:</strong>{" "}
                    {isApproved(req.data.loan_id) ? (
                      <span className="text-success fw-bold">Approved</span>
                    ) : (
                      <span className="text-warning fw-bold">Pending</span>
                    )}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default BorrowerDashboard;