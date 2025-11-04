from typing import Dict, Any, List
from datetime import datetime
from .base_contract import SmartContract

class EquipmentLeasingContract(SmartContract):
    def __init__(self, contract_id: str, owner: str, equipment_details: Dict[str, Any]):
        super().__init__(contract_id, owner)
        self.state.update({
            "equipment_details": equipment_details,
            "status": "AVAILABLE",
            "current_lease": None,
            "lease_history": [],
            "maintenance_records": [],
            "daily_rate": equipment_details.get("daily_rate"),
            "deposit_required": equipment_details.get("deposit_required", True)
        })

    def create_lease(self, lessee: str, lease_details: Dict[str, Any]) -> None:
        """Create a new lease for the equipment"""
        if self.state["status"] != "AVAILABLE":
            raise ValueError("Equipment is not available for lease")
        
        lease = {
            "lessee": lessee,
            "start_date": lease_details["start_date"],
            "end_date": lease_details["end_date"],
            "deposit_amount": lease_details.get("deposit_amount", 0),
            "daily_rate": self.state["daily_rate"],
            "status": "PENDING"
        }
        
        self.add_participant(lessee, "lessee")
        self.update_state("current_lease", lease)
        self.update_state("status", "PENDING_LEASE")
        self._emit_event("LeaseCreated", lease)

    def confirm_lease(self) -> None:
        """Confirm and activate a pending lease"""
        if self.state["status"] != "PENDING_LEASE":
            raise ValueError("No pending lease to confirm")
        
        current_lease = self.state["current_lease"]
        current_lease["status"] = "ACTIVE"
        self.update_state("current_lease", current_lease)
        self.update_state("status", "LEASED")
        self._emit_event("LeaseConfirmed", current_lease)

    def record_maintenance(self, maintenance_details: Dict[str, Any]) -> None:
        """Record maintenance performed on the equipment"""
        maintenance_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "details": maintenance_details
        }
        
        maintenance_records = self.state["maintenance_records"]
        maintenance_records.append(maintenance_record)
        self.update_state("maintenance_records", maintenance_records)
        self._emit_event("MaintenanceRecorded", maintenance_record)

    def end_lease(self, return_details: Dict[str, Any]) -> None:
        """End an active lease and record the return of equipment"""
        if self.state["status"] != "LEASED":
            raise ValueError("No active lease to end")
        
        current_lease = self.state["current_lease"]
        current_lease["status"] = "COMPLETED"
        current_lease["return_details"] = return_details
        current_lease["actual_return_date"] = datetime.utcnow().isoformat()
        
        lease_history = self.state["lease_history"]
        lease_history.append(current_lease)
        
        self.update_state("lease_history", lease_history)
        self.update_state("current_lease", None)
        self.update_state("status", "AVAILABLE")
        self._emit_event("LeaseEnded", {
            "lease": current_lease,
            "return_details": return_details
        })