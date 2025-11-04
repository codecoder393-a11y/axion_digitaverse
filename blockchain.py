import hashlib
import time
import json
import os
from collections import defaultdict

DIFFICULTY = 4
GAS_PER_TX = 1
MINING_REWARD = 10

# Defining the block structure
class Block:
    def __init__(self, index, previous_hash, timestamp, data, nonce, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        self.hash = hash

# Function to create hash for the block
def calculate_hash(index, previous_hash, timestamp, data, nonce):
    value = str(index) + previous_hash + str(timestamp) + json.dumps(data) + str(nonce)
    return hashlib.sha256(value.encode()).hexdigest()

# Function to create a genesis block
def create_genesis_block():
    return Block(0, "0", time.time(), {"type": "genesis"}, 0, "0")

# Defining the Blockchain
class Blockchain:

    # initializing the genesis block
    def __init__(self):
        self.chain = [create_genesis_block()]
        self.balances = defaultdict(lambda: 100)  # Initial acoin for demo

    def get_balance(self, address):
        return self.balances[address]

    # Function to add a block to the Blockchain
    def add_block(self, data, miner_address):
        last_block = self.chain[-1]
        index = last_block.index + 1
        timestamp = time.time()
        nonce, hash = self.proof_of_work(index, last_block.hash, timestamp, data)
        block = Block(index, last_block.hash, timestamp, data, nonce, hash)
        self.chain.append(block)
        self.update_balances(data, miner_address)
        return block

    # Proof of Work algorithm to find a valid nonce
    def proof_of_work(self, index, previous_hash, timestamp, data):
        nonce = 0
        while True:
            hash = calculate_hash(index, previous_hash, timestamp, data, nonce)
            if hash.startswith("0" * DIFFICULTY):
                return nonce, hash
            nonce += 1

    # Update balances of participants involved in the transaction
    def update_balances(self, data, miner_address):
        if data.get("type") == "transaction":
            sender = data["from"]
            recipient = data["to"]
            amount = data["amount"]
            gas = data["gas"]
            self.balances[sender] -= (amount + gas)
            self.balances[recipient] += amount
            self.balances[miner_address] += gas + MINING_REWARD
        elif data.get("type") == "loan_funding":
            lender = data["lender"]
            amount = data["amount"]
            self.balances[lender] -= amount
        elif data.get("type") == "loan_repayment":
            borrower = data["borrower"]
            lender = data["lender"]
            amount = data["amount"]
            self.balances[borrower] -= amount
            self.balances[lender] += amount

    # A function to add the entire blockchain data into dictionary/key value store format
    def to_dict(self):
        return [
            {
                "index": b.index,
                "previous_hash": b.previous_hash,
                "timestamp": b.timestamp,
                "data": b.data,
                "nonce": b.nonce,
                "hash": b.hash
            }
            for b in self.chain
        ]

# Function to create public/private key pairs
def generate_key_pair(username):
    salt = os.urandom(16).hex()
    private_key = hashlib.sha256((username + salt).encode()).hexdigest()
    public_key = hashlib.sha256(private_key.encode()).hexdigest()
    return public_key, private_key