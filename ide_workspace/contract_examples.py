from smart_contracts.contract_executor import ContractExecutor
from smart_contracts.tender_contract import TenderContract
from smart_contracts.real_estate_contract import RealEstateContract
from smart_contracts.equipment_leasing_contract import EquipmentLeasingContract
from smart_contracts.lending_contract import LendingContract
from axion_blockchain.core import Blockchain
from axion_vm import AxionVM
from datetime import datetime, timedelta

def example_tender_contract():
    # Initialize blockchain and VM
    blockchain = Blockchain()
    vm = AxionVM()
    executor = ContractExecutor(blockchain, vm)

    # Create a new tender contract
    tender_details = {
        "title": "Fuel Supply Tender",
        "description": "Supply of diesel fuel for government fleet",
        "submission_deadline": (datetime.utcnow() + timedelta(days=30)).timestamp(),
        "requirements": [
            "Minimum 100,000 liters monthly capacity",
            "Must have valid fuel trading license",
            "Must provide 24/7 delivery service"
        ]
    }

    # Create and execute the contract
    contract = TenderContract("TENDER-001", "ministry_of_transport", tender_details)
    
    # Submit a bid
    bid_details = {
        "company": "FuelCo Ltd",
        "price_per_liter": 1.45,
        "monthly_capacity": 150000,
        "delivery_terms": "24/7 delivery guaranteed"
    }
    
    # Execute and record the bid submission
    execution = executor.execute_contract(
        contract=contract,
        method_name="submit_bid",
        params={
            "bidder": "fuelco_ltd",
            "bid_details": bid_details
        }
    )

    # Verify the execution
    verification = executor.verify_execution("TENDER-001", "submit_bid")
    
    # Get contract history
    history = executor.get_contract_history("TENDER-001")
    
    return {
        "execution": execution,
        "verification": verification,
        "history": history
    }

def example_real_estate_contract():
    blockchain = Blockchain()
    vm = AxionVM()
    executor = ContractExecutor(blockchain, vm)

    # Create a new property listing
    property_details = {
        "title": "Modern Family Home",
        "location": "123 Sunshine Road, Harare",
        "price": 150000.00,
        "size": "250 sqm",
        "features": ["3 bedrooms", "2 bathrooms", "garage"],
        "coordinates": {"lat": -17.8292, "lon": 31.0522}
    }

    contract = RealEstateContract("PROP-001", "agent_smith", property_details)
    
    # Execute property verification
    execution = executor.execute_contract(
        contract=contract,
        method_name="verify_property",
        params={
            "verifier": "land_registry",
            "verification_result": True
        }
    )

    return {
        "execution": execution,
        "contract_state": contract.get_state()
    }

if __name__ == "__main__":
    # Run examples
    tender_result = example_tender_contract()
    print("Tender Contract Execution:", tender_result["execution"])
    
    real_estate_result = example_real_estate_contract()
    print("Real Estate Contract Execution:", real_estate_result["execution"])