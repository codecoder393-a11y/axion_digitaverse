

const loanRequests = [
  {
    id: 1,
    borrower: "John Doe",
    amount: 5000,
    purpose: "Business Expansion",
    status: "Pending",
  },
  {
    id: 2,
    borrower: "Jane Smith",
    amount: 3000,
    purpose: "Medical Expenses",
    status: "Pending",
  },
  {
    id: 3,
    borrower: "Tendai Doe",
    amount: 5000,
    purpose: "Business Expansion",
    status: "Pending",
  },
  {
    id: 4,
    borrower: "James Smith",
    amount: 3000,
    purpose: "Medical Expenses",
    status: "Pending",
  },
];

function LenderDashboard() {
  return (
    <body className="bg-primary-subtle">
    <div className="container py-5">
      <h2 className="mb-4 text-center">Lender Dashboard</h2>
      <div className="row">
        {loanRequests.map((request) => (
          <div className="col-md-6 mb-4" key={request.id}>
            <div className="card shadow">
              <div className="card-body">
                <h5 className="card-title">{request.borrower}</h5>
                <p className="card-text">
                  <strong>Amount:</strong> ${request.amount}
                  <br />
                  <strong>Purpose:</strong> {request.purpose}
                  <br />
                  <strong>Status:</strong> {request.status}
                </p>
                <button className="btn btn-primary">Send Loan Offer</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
    </body>
  );
}

export default LenderDashboard;