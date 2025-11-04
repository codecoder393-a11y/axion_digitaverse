from smart_contracts.contract_executor import ContractExecutor
from smart_contracts.tender_contract import TenderContract
from smart_contracts.real_estate_contract import RealEstateContract
from axion_blockchain.core import Blockchain
from axion_vm import AxionVM
from datetime import datetime, timedelta

def demonstrate_privacy_features():
    """
    Demonstrate Axion Digitaverse's privacy and security features
    """
    blockchain = Blockchain()
    vm = AxionVM()
    executor = ContractExecutor(blockchain, vm)

    # Example 1: Real Estate Contract with Private Data
    property_details = {
        "public_info": {
            "location": "123 Sunshine Road, Harare",
            "size": "250 sqm",
            "features": ["3 bedrooms", "2 bathrooms", "garage"]
        },
        "private_info": {
            "owner_identity": "Personal-ID-12345",
            "financial_records": "Bank-Statement-67890",
            "kyc_documents": "KYC-DOC-11111"
        }
    }

    contract = RealEstateContract("PROP-001", "agent_smith", property_details)
    
    # Execute with privacy protection
    execution = executor.execute_contract(
        contract=contract,
        method_name="verify_property",
        params={
            "verifier": "land_registry",
            "verification_result": True,
            "verification_documents": {
                "personal_id": "ID-VERIFICATION-DOC",
                "financial_check": "FINANCIAL-VERIFICATION-DOC"
            }
        }
    )

    # Example 2: Tender Contract with Sensitive Bid Data
    tender_details = {
        "public_info": {
            "title": "Fuel Supply Tender",
            "deadline": (datetime.utcnow() + timedelta(days=30)).timestamp(),
            "requirements": ["Valid license", "24/7 delivery"]
        },
        "private_info": {
            "budget_ceiling": "CONFIDENTIAL-BUDGET-001",
            "evaluation_criteria": "INTERNAL-DOC-002"
        }
    }

    tender_contract = TenderContract("TENDER-001", "ministry_of_transport", tender_details)
    
    # Submit bid with sensitive data protection
    bid_execution = executor.execute_contract(
        contract=tender_contract,
        method_name="submit_bid",
        params={
            "bidder": "fuelco_ltd",
            "bid_details": {
                "public_info": {
                    "company_name": "FuelCo Ltd",
                    "delivery_capacity": "150000L monthly"
                },
                "private_info": {
                    "price_structure": "CONFIDENTIAL-PRICE-001",
                    "financial_statements": "FINANCIAL-DOC-002",
                    "tax_clearance": "TAX-DOC-003"
                }
            }
        }
    )

    # Verify execution with zero-trust principles
    verification = executor.verify_execution("TENDER-001", "submit_bid")
    
    # Get audit trail
    audit_trail = executor.get_audit_trail("TENDER-001")

    return {
        "property_execution": execution,
        "tender_execution": bid_execution,
        "verification": verification,
        "audit_trail": audit_trail
    }

if __name__ == "__main__":
    results = demonstrate_privacy_features()
    
    print("\n=== Axion Digitaverse Privacy Demo ===")
    print("\nProperty Contract Execution:")
    print(f"Status: {results['property_execution']['status']}")
    print(f"Privacy Protection: Sensitive data stored off-chain")
    
    print("\nTender Contract Execution:")
    print(f"Status: {results['tender_execution']['status']}")
    print(f"Zero-Trust Verification: {results['verification']['verified']}")
    
    print("\nAudit Trail Sample:")
    for entry in results['audit_trail'][:2]:
        print(f"Action: {entry['action']}")
        print(f"Timestamp: {entry['timestamp']}")
        print(f"Audit Hash: {entry['audit_hash'][:16]}...")