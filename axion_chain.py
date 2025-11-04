import hashlib
import time
import json
import os

DIFFICULTY = 4
# GAS_FEE will be defined in main.py where it is used.
CHAIN_FILE = "blockchain.json"

class Block:
    def __init__(self, index, previous_hash, timestamp, data, nonce=0, hash=None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        self.hash = hash or self.calculate_hash()

    def calculate_hash(self):
        value = (
            str(self.index)
            + self.previous_hash
            + str(self.timestamp)
            + json.dumps(self.data, sort_keys=True)
            + str(self.nonce)
        )
        return hashlib.sha256(value.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data,
            "nonce": self.nonce,
            "hash": self.hash,
        }

    @staticmethod
    def from_dict(d):
        return Block(
            d["index"],
            d["previous_hash"],
            d["timestamp"],
            d["data"],
            d["nonce"],
            d["hash"],
        )

class Blockchain:
    def __init__(self):
        self.chain = []
        self.load_chain()

    def create_genesis_block(self):
        genesis_block = Block(
            index=0,
            previous_hash="0",
            timestamp=time.time(),
            data={"type": "genesis"},
            nonce=0,
        )
        self.chain.append(genesis_block)
        self.save_chain()

    def get_last_block(self):
        return self.chain[-1]

    def mine_block(self, data, miner_address=None):
        last_block = self.get_last_block()
        index = last_block.index + 1
        previous_hash = last_block.hash
        timestamp = time.time()

        # The data for the block is now a list of transactions
        block_data = [data]

        # New Reward Logic: Reward the miner with the transaction's gas fee.
        gas_fee = float(data.get("gas", 0))
        if miner_address and gas_fee > 0:
            reward_data = {
                "type": "reward",
                "to": miner_address,
                "amount": gas_fee
            }
            block_data.append(reward_data)

        nonce = 0
        while True:
            block = Block(index, previous_hash, timestamp, block_data, nonce)
            if block.hash.startswith("0" * DIFFICULTY):
                break
            nonce += 1

        self.chain.append(block)
        self.save_chain()
        return block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def hash_file(self, path: str) -> str:
        """Compute SHA-256 hash of a file. Exposed on the Blockchain API for convenience."""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def get_balance(self, address):
        balance = 0.0
        for block in self.chain:
            transactions = block.data if isinstance(block.data, list) else [block.data]
            for d in transactions:
                tx_type = d.get("type")
                if tx_type in ["mint", "reward"]:
                    if d.get("to") == address:
                        balance += float(d.get("amount", 0))
                elif tx_type == "transaction":
                    if d.get("from") == address:
                        balance -= float(d.get("amount", 0))
                        balance -= float(d.get("gas", 0))
                    if d.get("to") == address:
                        balance += float(d.get("amount", 0))
        return balance

    def save_chain(self):
        with open(CHAIN_FILE, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=2)

    def load_chain(self):
        if os.path.exists(CHAIN_FILE):
            try:
                with open(CHAIN_FILE, "r", encoding="utf-8") as f:
                    blocks = json.load(f)
                    self.chain = [Block.from_dict(b) for b in blocks]
            except (json.JSONDecodeError, TypeError):
                self.chain = []
        if not self.chain:
            self.create_genesis_block()

    def to_dict(self):
        return [block.to_dict() for block in self.chain]

def generate_key_pair(username):
    salt = os.urandom(16).hex()
    private_key = hashlib.sha256((username + salt).encode()).hexdigest()
    public_key = hashlib.sha256(private_key.encode()).hexdigest()
    return public_key, private_key
