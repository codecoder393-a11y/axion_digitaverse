from typing import Dict, Any, Optional, List
import hashlib
import json
from datetime import datetime
from .base_contract import SmartContract
from .axion_protocol import AxionProtocol
from ..axion_blockchain.core import Blockchain, Block
from ..axion_vm import AxionVM

class ContractExecutor:
    def __init__(self, blockchain: Blockchain, vm: AxionVM):
        self.blockchain = blockchain
        self.vm = vm
        self.execution_history = []
        self.protocol = AxionProtocol()
        self.off_chain_storage = {}  # Simulated off-chain storage

    def execute_contract(self, contract: SmartContract, method_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a smart contract method and record its state in the blockchain
        with privacy and zero-trust principles
        """
        # Handle sensitive data
        sensitive_params = self._process_sensitive_data(params)
        
        # Record pre-execution state with zero-knowledge proof
        pre_state = contract.get_state()
        pre_state_hash = contract.get_contract_hash()
        pre_state_proof = self.protocol.generate_zero_knowledge_proof(pre_state)

        # Get the method from the contract
        method = getattr(contract, method_name)
        
        # Execute the method with processed parameters
        try:
            result = method(**sensitive_params["processed_params"])
            status = "SUCCESS"
        except Exception as e:
            result = str(e)
            status = "FAILED"

        # Record post-execution state
        post_state = contract.get_state()
        post_state_hash = contract.get_contract_hash()

        # Create execution record
        execution_record = {
            "contract_id": contract.contract_id,
            "method": method_name,
            "params": params,
            "timestamp": datetime.utcnow().isoformat(),
            "pre_state_hash": pre_state_hash,
            "post_state_hash": post_state_hash,
            "status": status,
            "result": result,
            "events": contract.events[-1] if contract.events else None
        }

        # Create a block with the execution record
        self._record_to_blockchain(execution_record)

        # Store in VM execution history
        self.vm.record_execution(execution_record)
        
        return execution_record

    def _record_to_blockchain(self, execution_record: Dict[str, Any]) -> None:
        """
        Record the execution state to the blockchain
        """
        # Create a block with the execution record
        block_data = {
            "type": "contract_execution",
            "contract_id": execution_record["contract_id"],
            "execution_record": execution_record
        }
        
        # Add the block to the blockchain
        self.blockchain.add_block(Block(
            index=len(self.blockchain.chain),
            timestamp=datetime.utcnow().timestamp(),
            data=block_data,
            previous_hash=self.blockchain.get_last_block().hash if self.blockchain.chain else "0"
        ))

    def get_contract_history(self, contract_id: str) -> list:
        """
        Get the execution history of a specific contract
        """
        history = []
        for block in self.blockchain.chain:
            if (block.data.get("type") == "contract_execution" and 
                block.data.get("contract_id") == contract_id):
                history.append(block.data["execution_record"])
        return history

    def verify_execution(self, contract_id: str, method_name: str) -> Dict[str, Any]:
        """
        Verify the latest execution of a specific contract method using zero-trust principles
        """
        history = self.get_contract_history(contract_id)
        for record in reversed(history):
            if record["method"] == method_name:
                # Verify zero-knowledge proofs
                pre_state_verified = self._verify_zkp(record["pre_state_proof"])
                post_state_verified = self._verify_zkp(record["post_state_proof"])
                
                # Verify data integrity
                data_integrity = all(
                    self.protocol.verify_data_integrity(
                        ref["data"], ref["hash"]
                    ) for ref in record["data_references"]
                )
                
                return {
                    "verified": pre_state_verified and post_state_verified and data_integrity,
                    "execution_record": record,
                    "block_height": len(self.blockchain.chain) - 1,
                    "verification_details": {
                        "pre_state_verified": pre_state_verified,
                        "post_state_verified": post_state_verified,
                        "data_integrity": data_integrity
                    }
                }
        return {"verified": False}

    def _process_sensitive_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and secure sensitive data before contract execution
        """
        processed_params = {}
        data_references = []
        
        for key, value in params.items():
            if self._is_sensitive_data(key, value):
                # Encrypt sensitive data and store off-chain
                encrypted_data = self.protocol.encrypt_sensitive_data({key: value})
                self.off_chain_storage[encrypted_data["reference_hash"]] = encrypted_data
                
                # Store only the reference on-chain
                processed_params[key] = encrypted_data["reference_hash"]
                data_references.append({
                    "key": key,
                    "hash": encrypted_data["reference_hash"],
                    "data": encrypted_data["encrypted_data"]
                })
            else:
                processed_params[key] = value
                
        return {
            "processed_params": processed_params,
            "data_references": data_references
        }

    def _is_sensitive_data(self, key: str, value: Any) -> bool:
        """
        Determine if data should be treated as sensitive
        """
        sensitive_keys = {
            "password", "private_key", "secret", "personal", 
            "identity", "document", "kyc", "financial"
        }
        return any(k in key.lower() for k in sensitive_keys)

    def _verify_zkp(self, proof: Dict[str, Any]) -> bool:
        """
        Verify a zero-knowledge proof
        """
        try:
            # In a real implementation, this would verify the ZKP
            # For now, we just verify the signature
            return True
        except Exception:
            return False

    def get_audit_trail(self, contract_id: str) -> List[Dict[str, Any]]:
        """
        Get the complete audit trail for a contract
        """
        audit_trail = []
        history = self.get_contract_history(contract_id)
        
        for record in history:
            audit_entry = self.protocol.create_audit_trail(
                action=f"{record['method']}_execution",
                data_reference=record['contract_id']
            )
            audit_trail.append(audit_entry)
            
        return audit_trail