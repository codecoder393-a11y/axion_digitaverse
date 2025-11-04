from typing import Dict, Any, List
from datetime import datetime
from .base_contract import SmartContract

class TenderContract(SmartContract):
    def __init__(self, contract_id: str, owner: str, tender_details: Dict[str, Any]):
        super().__init__(contract_id, owner)
        self.state.update({
            "tender_details": tender_details,
            "status": "OPEN",
            "bids": [],
            "awarded_to": None,
            "submission_deadline": tender_details.get("submission_deadline"),
            "requirements": tender_details.get("requirements", [])
        })

    def submit_bid(self, bidder: str, bid_details: Dict[str, Any]) -> None:
        """Submit a bid for the tender"""
        if self.state["status"] != "OPEN":
            raise ValueError("Tender is not open for bids")
        
        if datetime.utcnow().timestamp() > self.state["submission_deadline"]:
            raise ValueError("Submission deadline has passed")

        bid = {
            "bidder": bidder,
            "details": bid_details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        bids = self.state["bids"]
        bids.append(bid)
        self.add_participant(bidder, "bidder")
        self.update_state("bids", bids)
        self._emit_event("BidSubmitted", {
            "bidder": bidder,
            "bid_details": bid_details
        })

    def evaluate_bid(self, bid_index: int, evaluation: Dict[str, Any]) -> None:
        """Record evaluation for a specific bid"""
        if self.state["status"] != "OPEN":
            raise ValueError("Tender is not in evaluation phase")
        
        bids = self.state["bids"]
        if bid_index >= len(bids):
            raise ValueError("Invalid bid index")
        
        bids[bid_index]["evaluation"] = evaluation
        self.update_state("bids", bids)
        self._emit_event("BidEvaluated", {
            "bid_index": bid_index,
            "evaluation": evaluation
        })

    def award_tender(self, winning_bidder: str) -> None:
        """Award the tender to a winning bidder"""
        if self.state["status"] != "OPEN":
            raise ValueError("Tender is not in award phase")
        
        self.update_state("status", "AWARDED")
        self.update_state("awarded_to", winning_bidder)
        self._emit_event("TenderAwarded", {"winner": winning_bidder})

    def complete_tender(self) -> None:
        """Mark the tender as complete"""
        if self.state["status"] != "AWARDED":
            raise ValueError("Tender has not been awarded")
        
        self.update_state("status", "COMPLETED")
        self._emit_event("TenderCompleted", {
            "winner": self.state["awarded_to"]
        })