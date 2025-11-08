from flask import Flask, request, jsonify
from flask_cors import CORS

import os
import sys
import json
from datetime import datetime

# Add parent directory to path so we can import from backend root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from axion_chain import Blockchain, generate_key_pair
from axion_ai import AxionAI
from axion_vm import AxionVM

app = Flask(__name__)
CORS(app)

# Initialize core components
blockchain = Blockchain()
axion_ai = AxionAI(blockchain)
axion_vm = AxionVM(blockchain)

# Constants
GAS_FEE = 0.01
SUPERUSER_BALANCE = 1_000_000.0

# Superuser keys 
SUPERUSER_PUBLIC_KEY = "a3a2afda3a17cc26ec134f7f1d09fe5c1615f0ba1ef2a2e4fe754e1987910b05"
SUPERUSER_PRIVATE_KEY = "3547423487c782ecb41223126b302ea8c0af5bcb7beaf58dc8882697094598f3"
SUPERUSER_USERNAME = "zimtechguru"

def get_miners():
    miners = set()
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get("type") == "register-miner":
                miners.add(tx.get("address"))
    return list(miners)

def get_random_miner():
    miners = get_miners()
    if not miners:
        return SUPERUSER_PUBLIC_KEY
    import random
    return random.choice(miners)

# Setup genesis user and balance
def setup_genesis_user_and_balance():
    if len(blockchain.chain) == 1:
        user_data = {
            "type": "user",
            "username": SUPERUSER_USERNAME,
            "profilePic": "",
            "address": SUPERUSER_PUBLIC_KEY,
            "privateKey": SUPERUSER_PRIVATE_KEY,
            "gas": 0
        }
        blockchain.mine_block(user_data, miner_address=None)
        mint_data = {
            "type": "mint",
            "to": SUPERUSER_PUBLIC_KEY,
            "amount": SUPERUSER_BALANCE,
            "gas": 0
        }
        blockchain.mine_block(mint_data, miner_address=None)

setup_genesis_user_and_balance()

# Routes
@app.route("/api/chain", methods=["GET"])
def get_chain():
    return jsonify(blockchain.to_dict())

@app.route("/api/wallet/<address>", methods=["GET"])
def get_wallet(address):
    balance = blockchain.get_balance(address)
    is_miner = address in get_miners()
    return jsonify({"address": address, "balance": balance, "is_miner": is_miner})

@app.route("/api/create-user", methods=["POST"])
def create_user():
    username = request.json["username"]
    public_key, private_key = generate_key_pair(username)
    user_data = {
        "type": "user",
        "username": username,
        "profilePic": "",
        "address": public_key,
        "privateKey": private_key,
        "gas": 0
    }
    blockchain.mine_block(user_data, miner_address=None)
    return jsonify({
        "message": "User created",
        "publicKey": public_key,
        "privateKey": private_key
    }), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    public_key = data.get("publicKey", "")
    private_key = data.get("privateKey", "")

    user_info = None
    for block in reversed(blockchain.chain):
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get("type") == "user" and tx.get("address") == public_key and tx.get("privateKey") == private_key:
                user_info = tx
                break
        if user_info:
            break
            
    if user_info:
        balance = blockchain.get_balance(public_key)
        is_miner = public_key in get_miners()
        return jsonify({
            "message": "Login successful", 
            "user": {
                "username": user_info.get("username"), 
                "address": public_key,
                "balance": balance,
                "isMiner": is_miner
            }
        }), 200

    return jsonify({"message": "Invalid credentials"}), 401

@app.route("/api/transaction", methods=["POST"])
def create_transaction():
    data = request.json
    sender = data["from"]
    recipient = data["to"]
    amount = float(data["amount"])
    miner = data.get("miner") or get_random_miner()

    if blockchain.get_balance(sender) < amount + GAS_FEE:
        return jsonify({"error": "Insufficient balance for transaction and gas fee"}), 400

    tx_data = {
        "type": "transaction",
        "from": sender,
        "to": recipient,
        "amount": amount,
        "gas": GAS_FEE
    }
    block = blockchain.mine_block(tx_data, miner_address=miner)
    return jsonify({"message": "Transaction successful", "block": block.to_dict()}), 201

@app.route("/api/miners", methods=["GET"])
def list_miners():
    return jsonify(get_miners())

@app.route("/api/register-miner", methods=["POST"])
def register_miner():
    data = request.json
    address = data.get("address")
    if not address:
        return jsonify({"error": "Address is required"}), 400

    if blockchain.get_balance(address) < GAS_FEE:
        return jsonify({"error": "Insufficient balance to register as a miner (gas fee)"}), 400

    miner_tx = {
        "type": "register-miner",
        "address": address,
        "gas": GAS_FEE
    }
    miner = get_random_miner()
    blockchain.mine_block(miner_tx, miner_address=miner)
    return jsonify({"message": f"Address {address} successfully registered as a miner."}), 201

@app.route("/api/axion-ai", methods=["POST"])
def axion_ai_chatbot():
    reply = axion_ai.ask(request.json.get("prompt", ""))
    return jsonify({"reply": reply})

@app.route("/api/axion-ai/dashboard", methods=["GET"])
def axion_ai_dashboard():
    report = axion_ai.data_science_report()
    return jsonify(report)