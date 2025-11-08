import { useEffect, useState } from "react";
import { useUser } from "../UserContext";
import { motion } from "framer-motion";
import { fetchApi, API_ENDPOINTS } from "../utils/api";

function RepayLoan() {
  const { user } = useUser();
  const [loans, setLoans] = useState<any[]>([]);
  const [status, setStatus] = useState("");
  const [selectedLoan, setSelectedLoan] = useState<any>(null);

  useEffect(() => {
    const fetchLoans = async () => {
      const res = await fetchApi(API_ENDPOINTS.CHAIN);
      const data = await res.json();
      // Find loans where this user is borrower and not yet repaid
      const requests = data.filter(
        (block: any) =>
          block.data.type === "loan_request" && block.data.borrower === user?.address
      );
      const approvals = data.filter((block: any) => block.data.type === "loan_approval");
      const repayments = data.filter((block: any) => block.data.type === "loan_repayment" && block.data.borrower === user?.address);

      // Only show loans that are approved and not yet repaid
      const repayable = requests
        .filter((req: any) =>
          approvals.some((appr: any) => appr.data.loan_id === req.data.loan_id) &&
          !repayments.some((rep: any) => rep.data.loan_id === req.data.loan_id)
        )
        .map((req: any) => {
          const loan = data.find((block: any) => block.data.type === "loan" && block.data.loan_id === req.data.loan_id);
          return loan ? { ...loan.data, loan_id: req.data.loan_id } : null;
        })
        .filter(Boolean);
      setLoans(repayable);
    };
    fetchLoans();
  }, [user]);

  const handleRepay = async (loan: any) => {
    setStatus("Processing...");
    const res = await fetchApi(API_ENDPOINTS.REPAY_LOAN, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        loan_id: loan.loan_id,
        borrower: user?.address,
        lender: loan.lender,
        amount: loan.amount
      })
    });
    if (res.ok) {
      setStatus("Loan repaid successfully!");
      setSelectedLoan(null);
    } else {
      const data = await res.json();
      setStatus(data.error || "Repayment failed");
    }
  };

  return (
    <div className="container py-5">
      <h2 className="mb-4 text-center text-white">Repay Loan</h2>
      {status && <div className="alert alert-info">{status}</div>}
      <div className="row">
        {loans.length === 0 && <div className="text-muted">No loans to repay.</div>}
        {loans.map((loan: any, idx: number) => (
          <motion.div
            className="col-md-6 mb-4"
            key={loan.loan_id}
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: idx * 0.1 }}
          >
            <div className="card shadow">
              <div className="card-body">
                <h5 className="card-title">Loan #{loan.loan_id}</h5>
                <p className="card-text">
                  <strong>Lender:</strong> {loan.lender}<br />
                  <strong>Amount:</strong> ${loan.amount}<br />
                  <strong>Rate:</strong> {loan.rate}%<br />
                  <strong>Duration:</strong> {loan.duration} months
                </p>
                <button
                  className="btn btn-success"
                  onClick={() => handleRepay(loan)}
                  disabled={selectedLoan === loan.loan_id}
                >
                  Repay Loan
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

export default RepayLoan;