from typing import Dict, Any, List
from datetime import datetime
from .base_contract import SmartContract

class RealEstateContract(SmartContract):
    def __init__(self, contract_id: str, owner: str, property_details: Dict[str, Any]):
        super().__init__(contract_id, owner)
        self.state.update({
            "property_details": property_details,
            "status": "LISTED",
            "verification_status": "PENDING",
            "price": property_details.get("price"),
            "documents": [],
            "buyer": None
        })

    def verify_property(self, verifier: str, verification_result: bool) -> None:
        """Verify the property listing by an authorized verifier"""
        self.add_participant(verifier, "verifier")
        self.update_state("verification_status", 
                         "VERIFIED" if verification_result else "REJECTED")
        self._emit_event("PropertyVerification", {
            "verifier": verifier,
            "result": verification_result
        })

    def add_document(self, document_hash: str, document_type: str) -> None:
        """Add a property document to the contract"""
        document = {
            "hash": document_hash,
            "type": document_type,
            "added_at": datetime.utcnow().isoformat()
        }
        documents = self.state["documents"]
        documents.append(document)
        self.update_state("documents", documents)

    def make_offer(self, buyer: str, offer_amount: float) -> None:
        """Record a buyer's offer for the property"""
        if self.state["verification_status"] != "VERIFIED":
            raise ValueError("Property not verified")
        
        self.add_participant(buyer, "potential_buyer")
        self._emit_event("OfferReceived", {
            "buyer": buyer,
            "amount": offer_amount
        })

    def accept_offer(self, buyer: str) -> None:
        """Accept an offer from a buyer"""
        if self.state["verification_status"] != "VERIFIED":
            raise ValueError("Property not verified")
        
        self.update_state("buyer", buyer)
        self.update_state("status", "UNDER_CONTRACT")
        self._emit_event("OfferAccepted", {"buyer": buyer})

    def complete_sale(self) -> None:
        """Mark the property sale as complete"""
        if self.state["status"] != "UNDER_CONTRACT":
            raise ValueError("Property not under contract")
        
        self.update_state("status", "SOLD")
        self._emit_event("SaleCompleted", {
            "buyer": self.state["buyer"],
            "price": self.state["price"]
        })