from typing import Dict, Any
from smart_contracts.base_contract import SmartContract

class MySmartContract(SmartContract):
    def __init__(self, contract_id: str, owner: str, initial_params: Dict[str, Any]):
        """
        Initialize your smart contract
        
        Parameters:
        - contract_id: Unique identifier for this contract
        - owner: Address of the contract owner
        - initial_params: Initial parameters for the contract
        """
        super().__init__(contract_id, owner)
        
        # Initialize contract state with your parameters
        self.state.update({
            "param1": initial_params.get("param1", "default_value"),
            "param2": initial_params.get("param2", 0),
            "status": "INITIALIZED"
        })
    
    def my_method(self, param1: str, param2: int) -> Dict[str, Any]:
        """
        Example method - replace with your own contract logic
        
        Parameters:
        - param1: First parameter description
        - param2: Second parameter description
        
        Returns:
        - Dictionary containing the result
        """
        # Update contract state
        self.update_state("param1", param1)
        self.update_state("param2", param2)
        
        # Emit an event
        self._emit_event("MyMethodCalled", {
            "param1": param1,
            "param2": param2
        })
        
        return {
            "success": True,
            "new_state": self.get_state()
        }
    
    def validate_state(self) -> bool:
        """
        Validate the contract's state
        Returns True if state is valid, False otherwise
        """
        required_fields = ["param1", "param2", "status"]
        return all(field in self.state for field in required_fields)