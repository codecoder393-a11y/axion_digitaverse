from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
from .base_contract import SmartContract

class LendingContract(SmartContract):
    def __init__(self, contract_id: str, owner: str, amount: Decimal, interest_rate: Decimal, duration_days: int):
        super().__init__(contract_id, owner)
        self.state.update({
            "amount": str(amount),
            "interest_rate": str(interest_rate),
            "duration_days": duration_days,
            "status": "CREATED",
            "borrower": None,
            "repayment_amount": str(amount * (1 + interest_rate)),
            "due_date": None
        })

    def fund_loan(self, lender: str) -> None:
        """Fund the loan by a lender"""
        if self.state["status"] != "CREATED":
            raise ValueError("Loan is not in CREATED state")
        self.add_participant(lender, "lender")
        self.update_state("status", "FUNDED")

    def accept_loan(self, borrower: str) -> None:
        """Accept the loan by a borrower"""
        if self.state["status"] != "FUNDED":
            raise ValueError("Loan is not in FUNDED state")
        self.add_participant(borrower, "borrower")
        due_date = datetime.utcnow().replace(
            hour=23, minute=59, second=59
        ).timestamp() + (self.state["duration_days"] * 86400)
        self.update_state("borrower", borrower)
        self.update_state("due_date", due_date)
        self.update_state("status", "ACTIVE")

    def repay_loan(self, amount: Decimal) -> None:
        """Process a loan repayment"""
        if self.state["status"] != "ACTIVE":
            raise ValueError("Loan is not active")
        current_repaid = Decimal(self.state.get("repaid_amount", "0"))
        new_repaid = current_repaid + amount
        self.update_state("repaid_amount", str(new_repaid))
        
        if new_repaid >= Decimal(self.state["repayment_amount"]):
            self.update_state("status", "COMPLETED")
            self._emit_event("LoanRepaid", {"final_amount": str(new_repaid)})