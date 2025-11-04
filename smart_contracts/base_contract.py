from typing import Dict, Any, Optional
from datetime import datetime
import json
import hashlib

class SmartContract:
    def __init__(self, contract_id: str, owner: str):
        self.contract_id = contract_id
        self.owner = owner
        self.created_at = datetime.utcnow().isoformat()
        self.state = {}
        self.participants = {owner: "owner"}
        self.events = []
        self.execution_context = None  # Will be set by ContractExecutor

    def set_execution_context(self, context: Dict[str, Any]) -> None:
        """Set the execution context for the contract"""
        self.execution_context = context

    def get_state(self) -> Dict[str, Any]:
        """Return the current state of the contract"""
        return {
            "contract_state": self.state,
            "participants": self.participants,
            "events": self.events,
            "last_updated": datetime.utcnow().isoformat(),
            "execution_context": self.execution_context
        }

    def update_state(self, key: str, value: Any) -> None:
        """Update a specific state variable"""
        self.state[key] = value
        self._emit_event("StateUpdate", {"key": key, "value": value})

    def add_participant(self, address: str, role: str) -> None:
        """Add a participant to the contract with a specific role"""
        self.participants[address] = role
        self._emit_event("ParticipantAdded", {"address": address, "role": role})

    def remove_participant(self, address: str) -> None:
        """Remove a participant from the contract"""
        if address in self.participants:
            del self.participants[address]
            self._emit_event("ParticipantRemoved", {"address": address})

    def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event to be recorded on the blockchain"""
        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "contract_id": self.contract_id,
            "data": data,
            "execution_context": self.execution_context
        }
        self.events.append(event)

    def serialize(self) -> str:
        """Serialize the contract state to JSON"""
        contract_data = {
            "contract_id": self.contract_id,
            "owner": self.owner,
            "created_at": self.created_at,
            "state": self.state,
            "participants": self.participants,
            "events": self.events
        }
        return json.dumps(contract_data)

    def deserialize(self, data: str) -> None:
        """Load contract state from JSON"""
        contract_data = json.loads(data)
        self.contract_id = contract_data["contract_id"]
        self.owner = contract_data["owner"]
        self.created_at = contract_data["created_at"]
        self.state = contract_data["state"]
        self.participants = contract_data["participants"]
        self.events = contract_data["events"]

    def get_contract_hash(self) -> str:
        """Generate a hash of the contract's current state"""
        return hashlib.sha256(self.serialize().encode()).hexdigest()