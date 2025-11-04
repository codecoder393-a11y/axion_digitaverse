# Axion Blockchain Core

A modular blockchain core for Axion Digitaverse, supporting key generation, transactions, mining, balances, and acoin payments.

## Usage

```python
from axion_blockchain import Blockchain, generate_key_pair

# Generate keys
pub, priv = generate_key_pair("partner_username")

# Initialize blockchain
bc = Blockchain()

# Register user
bc.add_user(pub)

# Create and mine a transaction
tx = bc.create_transaction(pub, "recipient_pubkey", 10)
block = bc.mine_block(tx, miner_address=pub)

# Check balance
print(bc.get_balance(pub))
```

# Axion Digitaverse Decentralized Node

## Start a node
```sh
python node.py 5000
```

## Add a peer (start another node)
```sh
python node.py 5001 http://localhost:5000
```

## API Endpoints
- POST /api/create-user { "username": "alice" }
- GET /api/wallet/<address>
- POST /api/transaction { "from": "...", "to": "...", "amount": 10 }
- POST /api/agent-deposit { "agent_address": "...", "user_address": "...", "amount": 10 }
- POST /api/python-exec { "code": "print(2+2)", "address": "..." }
- POST /api/add-peer { "peer_url": "http://localhost:5000" }
- GET /api/chain

---
## Credits

**Tendai Njanji**  
Blockchain Engineer, Software Engineer, Technopreneur  
Nickname: **zimtechguru**  
Email: njanjitendai02@gmail.com  
![Profile](backend\uploads\Facebook_creation_1057380959835973.jpeg)
---