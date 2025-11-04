from typing import Dict, Any, Type
import json
import sys
import os

# Add the backend directory to Python path to resolve imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from smart_contracts.base_contract import SmartContract
from smart_contracts.contract_executor import ContractExecutor
from axion_blockchain.core import Blockchain
from axion_vm import AxionVM

class ContractDevelopmentKit:
    def __init__(self):
        self.blockchain = Blockchain()
        self.vm = AxionVM()
        self.executor = ContractExecutor(self.blockchain, self.vm)
    
    def test_contract(self, contract_class, test_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test a smart contract in development
        """
        try:
            # Create contract instance
            contract = contract_class(
                contract_id="test_contract",
                owner="test_owner",
                initial_params=test_params.get("initial_params", {})
            )
            
            results = []
            
            # Run test methods
            for test in test_params.get("test_methods", []):
                method_name = test["method"]
                method_params = test["params"]
                
                # Execute the method
                execution = self.executor.execute_contract(
                    contract=contract,
                    method_name=method_name,
                    params=method_params
                )
                
                results.append({
                    "method": method_name,
                    "params": method_params,
                    "result": execution
                })
            
            return {
                "success": True,
                "test_results": results,
                "contract_state": contract.get_state(),
                "events": contract.events
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_contract(self, contract_class: Type[SmartContract]) -> Dict[str, Any]:
        """
        Validate a smart contract's structure and implementation
        """
        validation = {
            "has_init": hasattr(contract_class, "__init__"),
            "inherits_base": issubclass(contract_class, SmartContract),
            "has_validate_state": hasattr(contract_class, "validate_state"),
            "methods": []
        }
        
        # Check all public methods
        for attr_name in dir(contract_class):
            if not attr_name.startswith("_"):
                attr = getattr(contract_class, attr_name)
                if callable(attr):
                    validation["methods"].append({
                        "name": attr_name,
                        "doc": attr.__doc__,
                        "annotations": getattr(attr, "__annotations__", {})
                    })
        
        return validation

def example_usage():
    """
    Example of how to use the Contract Development Kit
    """
    # Import the template contract
    import os
    template_path = os.path.join(os.path.dirname(__file__), "templates", "contract_template.py")
    
    if os.path.exists(template_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("contract_template", template_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Initialize the kit
        cdk = ContractDevelopmentKit()
        
        # Example test parameters
        test_params = {
            "initial_params": {
                "param1": "initial_value",
                "param2": 42
            },
            "test_methods": [
                {
                    "method": "my_method",
                    "params": {
                        "param1": "new_value",
                        "param2": 100
                    }
                }
            ]
        }
        
        # Test the template contract
        test_results = cdk.test_contract(module.MySmartContract, test_params)
        print("\nTest Results:")
        print(json.dumps(test_results, indent=2))
        
        # Validate the contract
        validation_results = cdk.validate_contract(module.MySmartContract)
        print("\nValidation Results:")
        print(json.dumps(validation_results, indent=2))
    else:
        print(f"Template file not found at: {template_path}")

if __name__ == "__main__":
    example_usage()