# import time
# from .utils import generate_key_pair, calculate_hash

# class Block:
#     def __init__(self, index, previous_hash, timestamp, data, nonce, hash):
#         self.index = index
#         self.previous_hash = previous_hash
#         self.timestamp = timestamp
#         self.data = data
#         self.nonce = nonce
#         self.hash = hash

#     def to_dict(self):
#         return {
#             "index": self.index,
#             "previous_hash": self.previous_hash,
#             "timestamp": self.timestamp,
#             "data": self.data,
#             "nonce": self.nonce,
#             "hash": self.hash
#         }

# class Blockchain:
#     def __init__(self, difficulty=4, initial_balance=100):
#         self.difficulty = difficulty
#         self.chain = [self.create_genesis_block()]
#         self.balances = {}
#         self.initial_balance = initial_balance

#     def create_genesis_block(self):
#         return Block(0, "0", time.time(), {"type": "genesis"}, 0, "0")

#     def add_user(self, public_key):
#         if public_key not in self.balances:
#             self.balances[public_key] = self.initial_balance

#     def get_balance(self, address):
#         return self.balances.get(address, 0)

#     def create_transaction(self, sender, recipient, amount, gas=1):
#         if self.get_balance(sender) < amount + gas:
#             raise Exception("Insufficient balance")
#         tx = {
#             "type": "transaction",
#             "from": sender,
#             "to": recipient,
#             "amount": amount,
#             "gas": gas
#         }
#         return tx

#     def mine_block(self, data, miner_address):
#         last_block = self.chain[-1]
#         index = last_block.index + 1
#         timestamp = time.time()
#         nonce = 0
#         while True:
#             hash = calculate_hash(index, last_block.hash, timestamp, data, nonce)
#             if hash.startswith("0" * self.difficulty):
#                 break
#             nonce += 1
#         block = Block(index, last_block.hash, timestamp, data, nonce, hash)
#         self.chain.append(block)
#         self.update_balances(data, miner_address)
#         return block

#     def update_balances(self, data, miner_address):
#         if data.get("type") == "transaction":
#             sender = data["from"]
#             recipient = data["to"]
#             amount = data["amount"]
#             gas = data["gas"]
#             self.balances[sender] -= (amount + gas)
#             self.balances[recipient] = self.balances.get(recipient, 0) + amount
#             self.balances[miner_address] = self.balances.get(miner_address, 0) + gas + 10  # mining reward
#         elif data.get("type") == "agent_deposit":
#             agent = data["from"]
#             user = data["to"]
#             amount = data["amount"]
#             self.balances[agent] -= amount
#             self.balances[user] = self.balances.get(user, 0) + amount
#         elif data.get("type") == "python_exec":
#             pass

#     def to_dict(self):
#         return [block.to_dict() for block in self.chain]

#     def replace_chain(self, new_chain):
#         if len(new_chain) > len(self.chain):
#             self.chain = [Block(**b) for b in new_chain]
#             self.balances = {}
#             for block in self.chain:
#                 self.update_balances(block.data, block.data.get("from", "system"))