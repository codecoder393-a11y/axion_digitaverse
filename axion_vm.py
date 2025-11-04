import uuid

class AxionVM:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        # In-memory storage for deployed contracts
        # { "contract_address": { "code": "...", "instance": <object> } }
        self.contracts = {}

    def deploy_contract(self, contract_code, constructor_args):
        """
        Deploys a Python smart contract to the VM.
        This involves executing the code to define the class, creating an instance,
        and storing it.
        """
        try:
            # Generate a unique address for this contract instance
            contract_address = f"axion-{uuid.uuid4()}"

            # Create a sandboxed execution environment
            exec_globals = {
                'blockchain': self.blockchain
            }
            
            # Execute the code to define the contract class
            exec(contract_code, exec_globals)
            
            # Find the new class defined in the code
            class_name = [name for name in exec_globals if isinstance(exec_globals[name], type) and name != 'blockchain'][0]
            ContractClass = exec_globals[class_name]
            
            # Create an instance of the contract
            contract_instance = ContractClass(*constructor_args)
            
            # Store the contract code and instance
            self.contracts[contract_address] = {
                "code": contract_code,
                "instance": contract_instance
            }
            
            print(f"Deployed contract {class_name} to address {contract_address}")
            return contract_address, None
        except Exception as e:
            print(f"Error deploying contract: {e}")
            return None, str(e)

    def call_contract(self, contract_address, method_name, method_args):
        """
        Calls a method on a deployed smart contract.
        """
        try:
            contract_info = self.contracts.get(contract_address)
            if not contract_info:
                return None, f"Contract not found at address {contract_address}"
            
            instance = contract_info['instance']
            method = getattr(instance, method_name)
            
            # Call the method
            result = method(*method_args)
            
            return result, None
        except Exception as e:
            print(f"Error calling contract: {e}")
            return None, str(e)

    def get_contract_state(self, contract_address):
        """
        Retrieves the current state (instance variables) of a deployed contract.
        """
        contract_info = self.contracts.get(contract_address)
        if not contract_info or not hasattr(contract_info['instance'], '__dict__'):
            return None
        return contract_info['instance'].__dict__
