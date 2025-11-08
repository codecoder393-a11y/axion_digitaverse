
from flask import Flask, request, jsonify, send_from_directory, send_file  # type: ignore
import requests  # type: ignore
from flask_cors import CORS  # type: ignore
from axion_chain import Blockchain, generate_key_pair
from axion_ai import AxionAI
from axion_vm import AxionVM
from axion_blockchain.p2p import PeerNetwork
from axion_blockchain.file_storage import FileStorage
import os
import time
import sys
import io
import shutil
import random
import uuid
import json
import datetime

app = Flask(__name__)
CORS(app)

# --- ECONOMIC CONSTANTS ---
GAS_FEE = 0.01
SUPERUSER_BALANCE = 1_000_000.0

# --- INITIALIZE CORE COMPONENTS ---
blockchain = Blockchain()
axion_ai = AxionAI(blockchain)
axion_vm = AxionVM(blockchain)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
PROPERTY_UPLOADS = os.path.join(UPLOAD_FOLDER, "properties")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROPERTY_UPLOADS, exist_ok=True)
OFFCHAIN_MESSAGES_FILE = os.path.join(BASE_DIR, 'messages_offchain.json')

# --- INDEXES (file-backed) ---
INDEX_DIR = os.path.join(BASE_DIR, "indexes")
os.makedirs(INDEX_DIR, exist_ok=True)
PROPERTIES_INDEX = os.path.join(INDEX_DIR, "properties.json")
TENDERS_INDEX = os.path.join(INDEX_DIR, "tenders.json")
BIDS_INDEX = os.path.join(INDEX_DIR, "bids.json")

def _read_index(path):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def _write_index(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def append_to_index(path, obj):
    arr = _read_index(path)
    arr.append(obj)
    _write_index(path, arr)

# --- Initialize decentralized file storage (Axion Digitaverse storage) ---
peers = PeerNetwork()
file_storage = FileStorage(peers)


SUPERUSER_PUBLIC_KEY = "a3a2afda3a17cc26ec134f7f1d09fe5c1615f0ba1ef2a2e4fe754e1987910b05"
SUPERUSER_PRIVATE_KEY = "3547423487c782ecb41223126b302ea8c0af5bcb7beaf58dc8882697094598f3"
SUPERUSER_USERNAME = "zimtechguru"

IDE_ROOT = os.path.join(BASE_DIR, "ide_workspace")
os.makedirs(IDE_ROOT, exist_ok=True)

# --- MINER-RELATED HELPER FUNCTIONS ---

def compute_file_hash(path: str) -> str:
    """Compute SHA256 hash of a file. Used when Blockchain.hash_file is not available."""
    import hashlib
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


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
        return SUPERUSER_PUBLIC_KEY # Fallback to superuser if no miners are registered
    return random.choice(miners)

# --- GENESIS SETUP ---
def setup_genesis_user_and_balance():
    if len(blockchain.chain) == 1:
        user_data = {"type": "user", "username": SUPERUSER_USERNAME, "profilePic": "", "address": SUPERUSER_PUBLIC_KEY, "privateKey": SUPERUSER_PRIVATE_KEY, "gas": 0}
        blockchain.mine_block(user_data, miner_address=None)
        mint_data = {"type": "mint", "to": SUPERUSER_PUBLIC_KEY, "amount": SUPERUSER_BALANCE, "gas": 0}
        blockchain.mine_block(mint_data, miner_address=None)

setup_genesis_user_and_balance()

# --- MINER ENDPOINTS ---

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
    # The miner registration is mined by a random existing miner
    miner = get_random_miner()
    blockchain.mine_block(miner_tx, miner_address=miner)
    return jsonify({"message": f"Address {address} successfully registered as a miner."}), 201


# --- BLOCKCHAIN & WALLET ENDPOINTS ---

@app.route("/api/chain", methods=["GET"])
def get_chain():
    return jsonify(blockchain.to_dict())

@app.route("/api/wallet/<address>", methods=["GET"])
def get_wallet(address):
    balance = blockchain.get_balance(address)
    is_miner = address in get_miners()
    return jsonify({"address": address, "balance": balance, "is_miner": is_miner})

@app.route("/api/mint", methods=["POST"])
def mint():
    data = request.json
    to_address = data["to"]
    amount = float(data["amount"])
    mint_data = {"type": "mint", "to": to_address, "amount": amount, "gas": 0}
    blockchain.mine_block(mint_data, miner_address=None)
    return jsonify({"message": f"Minted {amount} to {to_address}"})

@app.route("/api/transaction", methods=["POST"])
def create_transaction():
    data = request.json
    sender = data["from"]
    recipient = data["to"]
    amount = float(data["amount"])
    miner = data.get("miner") or get_random_miner()

    if blockchain.get_balance(sender) < amount + GAS_FEE:
        return jsonify({"error": "Insufficient balance for transaction and gas fee"}), 400

    tx_data = {"type": "transaction", "from": sender, "to": recipient, "amount": amount, "gas": GAS_FEE}
    block = blockchain.mine_block(tx_data, miner_address=miner)
    return jsonify({"message": "Transaction successful", "block": block.to_dict()}), 201

# --- USER MANAGEMENT & PROFILE ---

@app.route("/api/create-user", methods=["POST"])
def create_user():
    username = request.json["username"]
    public_key, private_key = generate_key_pair(username)
    user_data = {"type": "user", "username": username, "profilePic": "", "address": public_key, "privateKey": private_key, "gas": 0}
    blockchain.mine_block(user_data, miner_address=None)
    return jsonify({"message": "User created", "publicKey": public_key, "privateKey": private_key}), 201

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
        # Find the latest profile picture for this address from chain (profile_update or user)
        profile_pic = user_info.get("profilePic", "")
        for block in reversed(blockchain.chain):
            transactions = block.data if isinstance(block.data, list) else [block.data]
            for tx in transactions:
                if tx.get("address") == public_key and tx.get("type") in ["profile_update", "user"]:
                    if tx.get("profilePic"):
                        profile_pic = tx.get("profilePic")
                        break
            if profile_pic:
                break

        balance = blockchain.get_balance(public_key)
        is_miner = public_key in get_miners()
        return jsonify({
            "message": "Login successful", 
            "user": {
                "username": user_info.get("username"), 
                "address": public_key, 
                "profilePic": profile_pic, 
                "balance": balance,
                "isMiner": is_miner
            }
        }), 200

    return jsonify({"message": "Invalid credentials"}), 401
    
@app.route("/api/upload-profile-pic", methods=["POST"])
def upload_profile_pic():
    address = request.form["address"]
    miner = request.form.get("miner") or get_random_miner()

    if blockchain.get_balance(address) < GAS_FEE:
        return jsonify({"error": "Insufficient balance for gas fee"}), 400

    if "profilePic" not in request.files:
        return jsonify({"error": "No file"}), 400
        
    file = request.files["profilePic"]
    filename = f'{address}_{int(time.time())}_{file.filename}'
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    
    pic_update_data = {"type": "profile_update", "address": address, "profilePic": filename, "gas": GAS_FEE}
    blockchain.mine_block(pic_update_data, miner_address=miner)
    return jsonify({"message": "Profile pic updated", "profilePic": filename}), 200

@app.route("/api/profile-pic/<address>", methods=["GET"])
def get_profile_pic(address):
    for block in reversed(blockchain.chain):
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get("type") in ["user", "profile_update"] and tx.get("address") == address:
                pic = tx.get("profilePic")
                if pic:
                    return send_from_directory(UPLOAD_FOLDER, pic)
    return "", 404


# Serve property uploads (images, request docs, transaction docs)
@app.route('/uploads/properties/<property_id>/<path:filename>', methods=['GET'])
def serve_property_file(property_id, filename):
    # filename may include subfolders like 'requests/<request_id>/file.pdf'
    prop_dir = os.path.join(PROPERTY_UPLOADS, property_id)
    # Protect against path traversal
    safe_path = os.path.normpath(os.path.join(prop_dir, filename))
    if not safe_path.startswith(os.path.normpath(prop_dir)):
        return jsonify({'error': 'Invalid filename'}), 400
    if not os.path.exists(safe_path):
        return "", 404
    dirpath = os.path.dirname(safe_path)
    fname = os.path.basename(safe_path)
    return send_from_directory(dirpath, fname)

@app.route("/api/contacts/add", methods=["POST"])
def add_contact():
    data = request.json
    user_address = data.get("user_address")
    contact_address = data.get("contact_address")
    miner = data.get("miner") or get_random_miner()

    if not user_address or not contact_address:
        return jsonify({"error": "User address and contact address are required"}), 400

    if blockchain.get_balance(user_address) < GAS_FEE:
        return jsonify({"error": "Insufficient balance to add a contact (gas fee)"}), 400

    contact_data = {
        "type": "add_contact",
        "user_address": user_address,
        "contact_address": contact_address,
        "gas": GAS_FEE,
    }
    
    block = blockchain.mine_block(contact_data, miner_address=miner)
    return jsonify({"message": "Contact added successfully", "block": block.to_dict()}), 201

@app.route("/api/contacts/<address>", methods=["GET"])
def get_contacts(address):
    contacts = []
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get("type") == "add_contact" and tx.get("user_address") == address:
                contacts.append(tx.get("contact_address"))
    
    # Now, for each contact address, let's fetch the user information
    contact_details = []
    for contact_address in contacts:
        user_info = None
        for block in reversed(blockchain.chain):
            transactions = block.data if isinstance(block.data, list) else [block.data]
            for tx in transactions:
                if tx.get("type") == "user" and tx.get("address") == contact_address:
                    user_info = {
                        "username": tx.get("username"),
                        "address": tx.get("address"),
                        "profilePic": tx.get("profilePic", "")
                    }
                    break
            if user_info:
                break
        if user_info:
            contact_details.append(user_info)

    return jsonify(contact_details)


# --- ADDITIVE ENDPOINTS FOR POSTS, MESSAGES AND CONTACT REMOVAL (mobile)
@app.route('/api/contacts/remove', methods=['POST'])
def remove_contact():
    data = request.json
    user_address = data.get('user_address')
    contact_address = data.get('contact_address')
    miner = data.get('miner') or get_random_miner()

    if not user_address or not contact_address:
        return jsonify({'error': 'User address and contact address are required'}), 400

    if blockchain.get_balance(user_address) < GAS_FEE:
        return jsonify({'error': 'Insufficient balance to remove a contact (gas fee)'}), 400

    contact_data = {
        'type': 'remove_contact',
        'user_address': user_address,
        'contact_address': contact_address,
        'gas': GAS_FEE,
    }
    block = blockchain.mine_block(contact_data, miner_address=miner)
    return jsonify({'message': 'Contact removed', 'block': block.to_dict()}), 200


@app.route('/api/post', methods=['POST'])
def create_post():
    data = request.get_json() or {}
    author = data.get('author')
    content = data.get('content')
    media = data.get('media', [])
    miner = data.get('miner') or get_random_miner()

    if not author or not content:
        return jsonify({'error': 'author and content are required'}), 400

    if blockchain.get_balance(author) < GAS_FEE:
        return jsonify({'error': 'Insufficient balance to create post (gas fee)'}), 400

    post_tx = {
        'type': 'post',
        'author': author,
        'content': content,
        'media': media,
        'timestamp': int(time.time()),
        'gas': GAS_FEE,
    }
    block = blockchain.mine_block(post_tx, miner_address=miner)
    return jsonify({'message': 'Post created', 'block': block.to_dict()}), 201


@app.route('/api/posts', methods=['GET'])
def list_posts():
    author = request.args.get('author')
    posts = []
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'post' and (not author or tx.get('author') == author):
                posts.append(tx)
    # sort by timestamp ascending
    posts = sorted(posts, key=lambda p: p.get('timestamp', 0))
    return jsonify(posts)


@app.route('/api/messages/send', methods=['POST'])
def send_message():
    data = request.get_json() or {}
    sender = data.get('from')
    recipient = data.get('to')
    text = data.get('text')
    miner = data.get('miner') or get_random_miner()

    if not sender or not recipient or text is None:
        return jsonify({'error': 'from, to and text are required'}), 400

    if blockchain.get_balance(sender) < GAS_FEE:
        return jsonify({'error': 'Insufficient balance to send message (gas fee)'}), 400

    # use deterministic conversation id for easier querying
    conv_id = '_'.join(sorted([sender, recipient]))
    msg_tx = {
        'type': 'message',
        'conversation_id': conv_id,
        'from': sender,
        'to': recipient,
        'text': text,
        'timestamp': int(time.time()),
        'gas': GAS_FEE,
    }
    block = blockchain.mine_block(msg_tx, miner_address=miner)
    return jsonify({'message': 'Message sent', 'block': block.to_dict(), 'conversation_id': conv_id}), 201


@app.route('/api/messages/<a>/<b>', methods=['GET'])
def get_messages_between(a, b):
    conv_id = '_'.join(sorted([a, b]))
    msgs = []
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'message' and tx.get('conversation_id') == conv_id:
                msgs.append(tx)
    msgs = sorted(msgs, key=lambda p: p.get('timestamp', 0))
    return jsonify(msgs)


def _load_offchain_messages():
    try:
        if os.path.exists(OFFCHAIN_MESSAGES_FILE):
            with open(OFFCHAIN_MESSAGES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return []


def _save_offchain_messages(msgs):
    try:
        with open(OFFCHAIN_MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(msgs, f, indent=2)
    except Exception:
        pass


@app.route('/api/messages/offchain/send', methods=['POST'])
def offchain_send_message():
    data = request.get_json() or {}
    sender = data.get('from')
    recipient = data.get('to')
    text = data.get('text')
    t = int(time.time())
    if not sender or not recipient or text is None:
        return jsonify({'error': 'from, to and text are required'}), 400
    conv_id = '_'.join(sorted([sender, recipient]))
    msg = {
        'id': str(uuid.uuid4()),
        'conversation_id': conv_id,
        'from': sender,
        'to': recipient,
        'text': text,
        'timestamp': t,
    }
    msgs = _load_offchain_messages()
    msgs.append(msg)
    _save_offchain_messages(msgs)
    return jsonify({'message': 'offchain message stored', 'msg': msg}), 201


@app.route('/api/messages/offchain/<a>/<b>', methods=['GET'])
def offchain_get_messages(a, b):
    conv_id = '_'.join(sorted([a, b]))
    msgs = _load_offchain_messages()
    out = [m for m in msgs if m.get('conversation_id') == conv_id]
    out = sorted(out, key=lambda p: p.get('timestamp', 0))
    return jsonify(out)

@app.route("/api/status", methods=["POST"])
def set_status():
    data = request.json
    address = data.get("address")
    status = data.get("status")
    miner = data.get("miner") or get_random_miner()

    if not address or not status:
        return jsonify({"error": "Address and status are required"}), 400

    if blockchain.get_balance(address) < GAS_FEE:
        return jsonify({"error": "Insufficient balance to set a status (gas fee)"}), 400

    status_data = {
        "type": "set_status",
        "address": address,
        "status": status,
        "gas": GAS_FEE,
    }
    
    block = blockchain.mine_block(status_data, miner_address=miner)
    return jsonify({"message": "Status set successfully", "block": block.to_dict()}), 201

@app.route("/api/status/<address>", methods=["GET"])
def get_status(address):
    latest_status = ""
    for block in reversed(blockchain.chain):
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get("type") == "set_status" and tx.get("address") == address:
                latest_status = tx.get("status")
                return jsonify({"status": latest_status})
    return jsonify({"status": ""})

# --- SMART CONTRACT ENDPOINTS (AXION VM) ---

@app.route("/api/contract/deploy", methods=["POST"])
def deploy_contract_endpoint():
    data = request.json
    contract_code = data.get("code", "")
    constructor_args = data.get("args", [])
    deployer_address = data.get("deployer")
    miner = data.get("miner") or get_random_miner()

    if not deployer_address:
        return jsonify({"error": "Deployer address is required"}), 400

    if blockchain.get_balance(deployer_address) < GAS_FEE:
        return jsonify({"error": "Insufficient balance to deploy contract (gas fee)"}), 400

    if not contract_code:
        return jsonify({"error": "Contract code is required"}), 400
        
    address, error = axion_vm.deploy_contract(contract_code, constructor_args)
    if error:
        return jsonify({"error": f"Failed to deploy contract: {error}"}), 500
        
    deployment_data = {"type": "deploy_contract", "contract_address": address, "code": contract_code, "constructor_args": constructor_args, "gas": GAS_FEE}
    blockchain.mine_block(deployment_data, miner_address=miner)
    return jsonify({"message": "Contract deployed successfully", "contract_address": address}), 201

@app.route("/api/contract/call", methods=["POST"])
def call_contract_endpoint():
    data = request.json
    contract_address = data.get("address")
    method_name = data.get("method")
    method_args = data.get("args", [])
    caller_address = data.get("caller")
    miner = data.get("miner") or get_random_miner()

    if not caller_address:
        return jsonify({"error": "Caller address is required"}), 400

    if blockchain.get_balance(caller_address) < GAS_FEE:
        return jsonify({"error": "Insufficient balance for contract call (gas fee)"}), 400

    result, error = axion_vm.call_contract(contract_address, method_name, method_args)
    if error:
        return jsonify({"error": f"Failed to call contract: {error}"}), 500
        
    call_data = {"type": "call_contract", "contract_address": contract_address, "method": method_name, "args": method_args, "result": result, "gas": GAS_FEE}
    blockchain.mine_block(call_data, miner_address=miner)
    return jsonify({"message": "Contract call successful", "result": result})

@app.route("/api/contract/<contract_address>", methods=["GET"])
def get_contract_state_endpoint(contract_address):
    state = axion_vm.get_contract_state(contract_address)
    if state is None: return jsonify({"error": "Contract not found"}), 404
    return jsonify({"contract_address": contract_address, "state": state})

@app.route("/api/contracts", methods=["GET"])
def get_all_contracts():
    return jsonify([{"address": addr, "state": axion_vm.get_contract_state(addr)} for addr in axion_vm.contracts])

# --- AXION AI ENDPOINTS ---
@app.route("/api/axion-ai", methods=["POST"])
def axion_ai_chatbot():
    reply = axion_ai.ask(request.json.get("prompt", ""))
    return jsonify({"reply": reply})

@app.route("/api/axion-ai/dashboard", methods=["GET"])
def axion_ai_dashboard():
    report = axion_ai.data_science_report()
    return jsonify(report)

# --- IDE & FILE MANAGEMENT ENDPOINTS ---
@app.route("/api/ide/run", methods=["POST"])
def ide_run():
    rel_path = request.json.get("path", "")
    abs_path = os.path.join(IDE_ROOT, rel_path)
    if not (abs_path.startswith(IDE_ROOT) and abs_path.endswith(".py")):
        return jsonify({"error": "Invalid path"}), 400
    if not os.path.isfile(abs_path):
        return jsonify({"error": "File not found"}), 404
    exec_globals = {'blockchain': blockchain}
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()
    try:
        with open(abs_path, "r", encoding="utf-8") as f: code = f.read()
        exec(code, exec_globals)
        output = mystdout.getvalue()
    except Exception as e:
        output = str(e)
    finally:
        sys.stdout = old_stdout
    return jsonify({"output": output})

@app.route("/api/ide/list", methods=["GET"])
def ide_list():
    def walk_dir(path):
        items = []
        for name in os.listdir(path):
            full = os.path.join(path, name)
            if os.path.isdir(full):
                items.append({"type": "folder", "name": name, "children": walk_dir(full)})
            else:
                items.append({"type": "file", "name": name})
        return items
    return jsonify(walk_dir(IDE_ROOT))

@app.route("/api/ide/open", methods=["POST"])
def ide_open():
    rel_path = request.json.get("path", "")
    abs_path = os.path.join(IDE_ROOT, rel_path)
    if not abs_path.startswith(IDE_ROOT): return jsonify({"error": "Invalid path"}), 400
    if not os.path.isfile(abs_path): return jsonify({"error": "File not found"}), 404
    with open(abs_path, "r", encoding="utf-8") as f:
        return jsonify({"content": f.read()})

@app.route("/api/ide/save", methods=["POST"])
def ide_save():
    rel_path = request.json.get("path", "")
    content = request.json.get("content", "")
    abs_path = os.path.join(IDE_ROOT, rel_path)
    if not abs_path.startswith(IDE_ROOT): return jsonify({"error": "Invalid path"}), 400
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f: f.write(content)
    return jsonify({"message": "Saved"})

# --TENDER ENDPOINTS ---
# Endpoint to create a tender on Blockchain
def generate_unique_id():
    return str(uuid.uuid4())


def derive_public_from_private(private_key: str) -> str:
    import hashlib as _hashlib
    return _hashlib.sha256(private_key.encode()).hexdigest()


# --- Demo signature helpers (transitional) ---
def _get_private_for_public(public_key: str):
    # Find the user's privateKey stored in the chain (legacy behavior)
    for block in reversed(blockchain.chain):
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get("type") == "user" and tx.get("address") == public_key:
                return tx.get("privateKey")
    return None

def compute_demo_signature(private_key: str, payload_str: str) -> str:
    # Deterministic demo signature: sha256(private_key + payload_str)
    import hashlib as _hashlib
    return _hashlib.sha256((private_key + payload_str).encode()).hexdigest()

def verify_demo_signature(public_key: str, payload_str: str, signature: str) -> bool:
    # Retrieve stored privateKey for public_key (legacy) and recompute
    private = _get_private_for_public(public_key)
    if not private:
        return False
    expected = compute_demo_signature(private, payload_str)
    return expected == signature

@app.route('/api/create_tender', methods=['POST'])
def create_tender():
    data = request.get_json() or {}
    tender_id = generate_unique_id()
    # Require issuer address (publicKey) and signature instead of privateKey
    issuer = data.get("issuer")
    signature = data.get("signature")
    if not issuer or not signature:
        return jsonify({"error": "Issuer publicKey and signature are required"}), 400

    # Allow legacy privateKey (backwards compatibility) OR new signature flow
    private_key = data.get("privateKey")
    payload = {
        "title": data.get("title"),
        "description": data.get("description"),
        "deadline": data.get("deadline"),
        "issuer": issuer,
        "documents": data.get("documents"),
    }
    # Use compact separators to match JS JSON.stringify output (no spaces)
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))

    verified = False
    if private_key:
        # Legacy: verify private_key corresponds to issuer public key
        if derive_public_from_private(private_key) != issuer:
            return jsonify({"error": "Invalid privateKey for issuer"}), 403
        verified = True
    else:
        # New flow: signature must be provided
        if not verify_demo_signature(issuer, payload_str, signature):
            return jsonify({"error": "Invalid signature for issuer"}), 403
        verified = True

    # Verify issuer exists as a registered user in the chain
    def user_exists(address):
        for block in reversed(blockchain.chain):
            transactions = block.data if isinstance(block.data, list) else [block.data]
            for tx in transactions:
                if tx.get("type") == "user" and tx.get("address") == address:
                    return True
        return False

    if not user_exists(issuer):
        return jsonify({"error": "Issuer not found. Please sign up / login."}), 403

    # Store structured tender data on-chain. Include type for easy querying by front-end.
    tender_data = {
        "type": "tender",
        "tender_id": tender_id,
        "title": payload["title"],
        "description": payload["description"],
        "deadline": payload["deadline"],
        "issuer": issuer,
        "documents": payload["documents"],
        "created_at": int(time.time()),
    }
    # Mine the tender data into the blockchain
    blockchain.mine_block(tender_data, miner_address=None)

    # Append to tender index for fast listing
    try:
        append_to_index(TENDERS_INDEX, tender_data)
    except Exception:
        pass

    return jsonify({"message": "Tender created in Blockchain", "tender_id": tender_id}), 201


@app.route('/api/tenders/<tender_id>/bid', methods=['POST'])
def submit_bid(tender_id):
    data = request.get_json() or {}
    bidder = data.get('bidder')
    signature = data.get('signature')
    amount = data.get('amount')
    metadata = data.get('metadata', {})

    # Accept legacy privateKey OR new signature
    private_key = data.get('privateKey')
    if not bidder or amount is None or (not signature and not private_key):
        return jsonify({'error': 'Bidder, amount and signature/privateKey are required'}), 400

    # Find tender and its issuer
    tender_tx = None
    for block in reversed(blockchain.chain):
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'tender' and tx.get('tender_id') == tender_id:
                tender_tx = tx
                break
        if tender_tx:
            break

    if not tender_tx:
        return jsonify({'error': 'Tender not found'}), 404

    issuer = tender_tx.get('issuer')
    if issuer == bidder:
        return jsonify({'error': 'Tender creator cannot bid on their own tender'}), 403

    # Verify bidder exists
    def user_exists(address):
        for block in reversed(blockchain.chain):
            transactions = block.data if isinstance(block.data, list) else [block.data]
            for tx in transactions:
                if tx.get("type") == "user" and tx.get("address") == address:
                    return True
        return False

    if not user_exists(bidder):
        return jsonify({'error': 'Bidder not registered'}), 403

    # Verify signature over canonical payload (tender_id, bidder, amount, metadata)
    payload = {
        'tender_id': tender_id,
        'bidder': bidder,
        'amount': float(amount),
        'metadata': metadata
    }
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    if private_key:
        # legacy verification
        if derive_public_from_private(private_key) != bidder:
            return jsonify({'error': 'Invalid privateKey for bidder'}), 403
    else:
        if not verify_demo_signature(bidder, payload_str, signature):
            return jsonify({'error': 'Invalid signature for bidder'}), 403

    bid_data = {
        'type': 'bid',
        'tender_id': tender_id,
        'bidder': bidder,
        'amount': float(amount),
        'metadata': metadata,
        'timestamp': int(time.time())
    }

    blockchain.mine_block(bid_data, miner_address=None)

    # Append to bids index
    try:
        append_to_index(BIDS_INDEX, bid_data)
    except Exception:
        pass

    return jsonify({'message': 'Bid submitted successfully'}), 201


@app.route('/api/tenders', methods=['GET'])
def list_tenders():
    # Prefer fast file-backed index
    tenders = _read_index(TENDERS_INDEX)
    if tenders:
        return jsonify(tenders)

    # Fallback to scanning chain
    tenders = []
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'tender':
                tenders.append(tx)
    return jsonify(tenders)


@app.route('/api/tenders/<tender_id>/bids', methods=['GET'])
def list_bids_for_tender(tender_id):
    # Prefer file-backed index
    bids = _read_index(BIDS_INDEX)
    if bids:
        return jsonify([b for b in bids if b.get('tender_id') == tender_id])

    # Fallback to scanning chain
    bids = []
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'bid' and tx.get('tender_id') == tender_id:
                bids.append(tx)
    return jsonify(bids)


@app.route('/api/upload_docs', methods=['POST'])
def upload_docs():
    # Accept multipart/form-data with 'address' field and files: tax_clearance and company_docs (multiple)
    address = request.form.get('address')
    public_key = request.form.get('publicKey')
    signature = request.form.get('signature')
    if not address:
        return jsonify({'error': 'Address is required'}), 400

    # Verify signature if provided
    # Build filenames list for canonical payload
    filenames = [f.filename for f in request.files.values() if f]
    payload = {"address": address, "filenames": filenames}
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    private_key = request.form.get('privateKey')
    if public_key:
        if public_key != address:
            return jsonify({'error': 'publicKey must match address'}), 400
        if not signature or not verify_demo_signature(public_key, payload_str, signature):
            return jsonify({'error': 'Invalid signature for upload'}), 403
    elif private_key:
        # legacy verification
        if derive_public_from_private(private_key) != address:
            return jsonify({'error': 'Invalid privateKey for upload address'}), 403

    # Verify user exists
    def user_exists(address):
        for block in reversed(blockchain.chain):
            transactions = block.data if isinstance(block.data, list) else [block.data]
            for tx in transactions:
                if tx.get("type") == "user" and tx.get("address") == address:
                    return True
        return False

    if not user_exists(address):
        return jsonify({'error': 'User not registered'}), 403

    saved_files = []
    for key in request.files:
        file = request.files[key]
        if file:
            filename = f'{address}_{int(time.time())}_{file.filename}'
            temp_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(temp_path)
            # Split into chunks and store on Axion decentralized storage
            try:
                chunks = file_storage.split_file(temp_path)
                file_storage.store_chunks(chunks)
                chunk_hashes = [c[0] for c in chunks]
            except Exception as e:
                # cleanup temp and return error
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
                return jsonify({'error': f'Failed to store file in decentralized storage: {e}'}), 500
            # cleanup temp file
            try:
                os.remove(temp_path)
            except Exception:
                pass
            saved_files.append({'field': key, 'filename': filename, 'chunk_hashes': chunk_hashes})

    # Store a document_upload tx on-chain with file hashes for auditability; files are stored in uploads folder
    doc_tx = {
        'type': 'document_upload',
        'address': address,
        'files': saved_files,
        'timestamp': int(time.time())
    }
    blockchain.mine_block(doc_tx, miner_address=None)
    return jsonify({'message': 'Files uploaded and anchored', 'files': saved_files}), 201



# --- REAL ESTATE ENDPOINTS ---

@app.route("/api/properties", methods=["GET"])
def get_properties():
    """Get all listed properties"""
    # Prefer file-backed index for speed
    properties = _read_index(PROPERTIES_INDEX)
    if properties:
        return jsonify(properties)

    # Fallback to scanning the chain
    properties = []
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get("type") == "property":
                properties.append(tx)
    return jsonify(properties)

@app.route("/api/properties/<property_id>", methods=["GET"])
def get_property(property_id):
    """Get details of a specific property"""
    # Check index first for efficiency
    try:
        index_props = _read_index(PROPERTIES_INDEX)
        if index_props:
            prop = next((p for p in index_props if p.get("id") == property_id), None)
            if prop:
                # Also add latest owner status from chain
                for block in reversed(blockchain.chain):
                    transactions = block.data if isinstance(block.data, list) else [block.data]
                    for tx in transactions:
                        if tx.get("type") == "set_status" and tx.get("address") == prop.get("owner_public_key"):
                            prop["owner_status"] = tx.get("status")
                            break
                    if "owner_status" in prop:
                        break
                return jsonify(prop)
    except Exception:
        pass

    # Fallback to scanning blockchain
    prop = None
    # Get original property record first
    for block in reversed(blockchain.chain):
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get("type") == "property" and tx.get("id") == property_id:
                prop = tx.copy()
                break
        if prop:
            break

    if not prop:
        return jsonify({"error": "Property not found"}), 404

    # Apply all updates and transfers to get latest state
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get("type") == "property_update" and tx.get("property_id") == property_id:
                updates = tx.get("updates", {})
                prop.update(updates)
                prop["updated_at"] = tx.get("updated_at", prop.get("updated_at"))
            elif tx.get("type") == "property_transfer" and tx.get("property_id") == property_id:
                prop["owner_public_key"] = tx.get("to")
                prop["status"] = "sold"
                prop["last_sale"] = {
                    "amount": tx.get("amount"),
                    "timestamp": tx.get("timestamp"),
                    "transaction_id": tx.get("transaction_id")
                }

    # Get latest owner status
    for block in reversed(blockchain.chain):
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get("type") == "set_status" and tx.get("address") == prop.get("owner_public_key"):
                prop["owner_status"] = tx.get("status")
                break
        if "owner_status" in prop:
            break

    return jsonify(prop)


@app.route('/api/properties/<property_id>/analysis', methods=['GET'])
def property_analysis(property_id):
    """Return a lightweight market analysis for the property.
    This is a heuristic/demo implementation that uses historical on-chain entries to build
    a price history and a deterministic predicted value plus nearby-amenities mock data.
    """
    # Find the base property record
    prop = None
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'property' and tx.get('id') == property_id:
                prop = tx.copy()
    if not prop:
        return jsonify({'error': 'Property not found'}), 404

    # Build price history: start with the original price and include any property_update price changes
    price_history = []
    try:
        orig_price = float(prop.get('price', 0))
    except Exception:
        orig_price = 0.0
    created_at = prop.get('created_at') or ''
    if created_at:
        price_history.append({'date': created_at, 'price': orig_price})

    # Look for updates and transactions that affect price
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'property_update' and tx.get('property_id') == property_id:
                updates = tx.get('updates', {})
                if 'price' in updates:
                    price_history.append({'date': tx.get('updated_at') or '', 'price': updates.get('price')})
            if tx.get('type') == 'property_transaction' and tx.get('property_id') == property_id:
                # record transaction price as an observed price point
                price_history.append({'date': tx.get('timestamp') or '', 'price': tx.get('amount')})

    # If no rich history, create a few synthetic points around orig_price
    if len(price_history) < 2:
        now = datetime.datetime.utcnow().isoformat()
        price_history = [
            {'date': created_at or now, 'price': orig_price},
            {'date': now, 'price': round(orig_price * 1.02, 2)}
        ]

    # Compute a simple predicted value: trend-based linear extrapolation over history
    try:
        first = price_history[0]['price']
        last = price_history[-1]['price']
        # percent change
        change = 0.0
        if first > 0:
            change = (last - first) / first
        predicted = round(last * (1 + change * 0.5), 2)
    except Exception:
        predicted = prop.get('price', 0)

    # Market trends: derive some mock trends from price movement
    market_trends = []
    pct_change = 0.0
    try:
        pct_change = round(((price_history[-1]['price'] - price_history[0]['price']) / max(1, price_history[0]['price'])) * 100, 2)
    except Exception:
        pct_change = 0.0
    market_trends.append({'trend': 'Local price change (history)', 'value': price_history[-1]['price'], 'change': pct_change})
    market_trends.append({'trend': 'Supply tightness', 'value': 0.7, 'change': 5})
    market_trends.append({'trend': 'Demand growth (yearly)', 'value': 0.12, 'change': 12})

    # Nearby amenities: deterministic pseudo-random based on location string
    import hashlib
    h = hashlib.sha256((prop.get('location', '') or '').encode()).hexdigest()
    seed = int(h[:8], 16)
    amenities = ['School', 'Hospital', 'Shopping Mall', 'Metro Station', 'Park']
    nearby = []
    for i, a in enumerate(amenities):
        dist = round(((seed >> (i * 4)) & 0xF) % 10 + 0.5, 1)
        rating = ((seed >> (i * 3)) & 0x3) + 3
        nearby.append({'type': a, 'distance': dist, 'rating': rating})

    result = {
        'predictedValue': predicted,
        'priceHistory': price_history,
        'marketTrends': market_trends,
        'nearbyAmenities': nearby
    }
    return jsonify(result)


@app.route('/api/properties/<property_id>/verification', methods=['GET'])
def property_verification(property_id):
    """Return verification info: title verification flag, ownership history, and documents with hashes.
    This collates information already present on-chain.
    """
    # Locate property
    prop = None
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'property' and tx.get('id') == property_id:
                prop = tx.copy()
    if not prop:
        return jsonify({'error': 'Property not found'}), 404

    # Build ownership history: look for property creation and transfers
    ownership_history = []
    # creation
    owner = prop.get('owner_public_key')
    created = prop.get('created_at') or ''
    ownership_history.append({'owner': owner, 'from': '', 'to': created, 'transactionHash': ''})

    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'property_transfer' and tx.get('property_id') == property_id:
                ownership_history.append({
                    'owner': tx.get('to'),
                    'from': tx.get('timestamp') or '',
                    'to': tx.get('timestamp') or '',
                    'transactionHash': tx.get('transaction_id') or ''
                })

    # Documents: include initial property documents and any document_upload / transaction_documents entries referencing this property
    documents = []
    # Start with property documents
    for d in prop.get('documents', []):
        documents.append({'name': d.get('title'), 'hash': d.get('hash'), 'verified': d.get('verified', False), 'timestamp': prop.get('created_at')})

    # Scan chain for transaction_documents and document_upload that may include this property's files
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'transaction_documents':
                # find transaction -> property mapping
                tx_id = tx.get('transaction_id')
                # try to find associated transaction to get property id
                assoc_tx = None
                for b2 in blockchain.chain:
                    for t2 in (b2.data if isinstance(b2.data, list) else [b2.data]):
                        if t2.get('type') == 'property_transaction' and t2.get('id') == tx_id:
                            assoc_tx = t2
                            break
                    if assoc_tx:
                        break
                if assoc_tx and assoc_tx.get('property_id') == property_id:
                    for f in tx.get('files', []):
                        documents.append({'name': f.get('filename'), 'hash': f.get('hash'), 'verified': False, 'timestamp': tx.get('timestamp')})
            if tx.get('type') == 'document_upload' and tx.get('address') == prop.get('owner_public_key'):
                for f in tx.get('files', []):
                    documents.append({'name': f.get('filename'), 'hash': f.get('chunk_hashes', [None])[0], 'verified': False, 'timestamp': tx.get('timestamp')})

    # Decide titleVerified: very simple check — if the property has any transfer or a document with 'title' in name
    title_verified = any('title' in (d.get('name') or '').lower() for d in documents) or len(ownership_history) > 0

    result = {
        'titleVerified': bool(title_verified),
        'ownershipHistory': ownership_history,
        'documents': documents
    }
    return jsonify(result)
@app.route("/api/properties/submit", methods=["POST"])
def submit_property():
    """Submit a new property listing"""
    if "images" not in request.files:
        return jsonify({"error": "No images provided"}), 400
    
    owner_public_key = request.form.get("owner_public_key")
    if not owner_public_key:
        return jsonify({"error": "Owner public key is required"}), 400

    if blockchain.get_balance(owner_public_key) < GAS_FEE:
        return jsonify({"error": "Insufficient balance for property submission"}), 400

    property_id = str(uuid.uuid4())
    property_dir = os.path.join(PROPERTY_UPLOADS, property_id)
    os.makedirs(property_dir, exist_ok=True)

    # Process images
    images = request.files.getlist("images")
    image_paths = []
    for image in images:
        filename = f"{uuid.uuid4()}_{image.filename}"
        image_path = os.path.join(property_dir, filename)
        image.save(image_path)
        image_paths.append(f"/uploads/properties/{property_id}/{filename}")

    # Process documents
    document_data = []
    if "documents" in request.files:
        documents = request.files.getlist("documents")
        for doc in documents:
            filename = f"{uuid.uuid4()}_{doc.filename}"
            doc_path = os.path.join(property_dir, filename)
            doc.save(doc_path)
            # Create document hash for verification
            try:
                # Prefer blockchain-provided helper if available
                doc_hash = getattr(blockchain, 'hash_file', compute_file_hash)(doc_path)
            except Exception:
                doc_hash = compute_file_hash(doc_path)
            document_data.append({
                "title": doc.filename,
                "hash": doc_hash,
                "verified": False
            })

    # Create property record
    property_data = {
        "type": "property",
        "id": property_id,
        "title": request.form.get("title"),
        "price": float(request.form.get("price")),
        "location": request.form.get("location"),
        "description": request.form.get("description"),
        "owner_public_key": owner_public_key,
        "verified": False,
        "status": "available",
        "images": image_paths,
        "documents": document_data,
    "created_at": datetime.datetime.utcnow().isoformat(),
    "updated_at": datetime.datetime.utcnow().isoformat(),
        "gas": GAS_FEE
    }

    # Store in blockchain
    miner = get_random_miner()
    blockchain.mine_block(property_data, miner_address=miner)

    # Append to properties index for fast listing
    try:
        append_to_index(PROPERTIES_INDEX, property_data)
    except Exception:
        pass

    return jsonify({"status": "success", "property_id": property_id})

@app.route("/api/transactions/initiate", methods=["POST"])
def initiate_property_transaction():
    """Initiate a property transaction"""
    data = request.json
    buyer_public_key = data.get("buyer_public_key")
    property_id = data.get("property_id")
    
    if not buyer_public_key or not property_id:
        return jsonify({"error": "Buyer public key and property ID are required"}), 400

    # Verify buyer has sufficient balance
    property_data = None
    for block in reversed(blockchain.chain):
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get("type") == "property" and tx.get("id") == property_id:
                property_data = tx
                break
        if property_data:
            break

    if not property_data:
        return jsonify({"error": "Property not found"}), 404

    price = property_data.get("price", 0)
    if blockchain.get_balance(buyer_public_key) < price + GAS_FEE:
        return jsonify({"error": "Insufficient balance for property purchase"}), 400

    transaction_id = str(uuid.uuid4())
    transaction_data = {
        "type": "property_transaction",
        "id": transaction_id,
        "property_id": property_id,
        "buyer_public_key": buyer_public_key,
        "seller_public_key": property_data["owner_public_key"],
        "amount": price,
        "status": "pending",
    "timestamp": datetime.datetime.utcnow().isoformat(),
        "gas": GAS_FEE
    }

    miner = get_random_miner()
    blockchain.mine_block(transaction_data, miner_address=miner)

    return jsonify({"status": "success", "transaction_id": transaction_id})


@app.route('/api/properties/request-purchase', methods=['POST'])
def request_purchase():
    """Buyer requests to purchase a property (can attach documents)."""
    # Accept multipart/form-data: property_id, buyer_public_key, amount, message, files...
    property_id = request.form.get('property_id')
    buyer = request.form.get('buyer_public_key')
    amount = request.form.get('amount')
    message = request.form.get('message', '')

    if not property_id or not buyer or not amount:
        return jsonify({'error': 'property_id, buyer_public_key and amount are required'}), 400

    # Verify buyer exists
    def user_exists(address):
        for block in reversed(blockchain.chain):
            transactions = block.data if isinstance(block.data, list) else [block.data]
            for tx in transactions:
                if tx.get('type') == 'user' and tx.get('address') == address:
                    return True
        return False

    if not user_exists(buyer):
        return jsonify({'error': 'Buyer not registered'}), 403

    # --- Verify signature / privateKey for buyer (require signed request) ---
    signature = request.form.get('signature')
    private_key = request.form.get('privateKey')
    filenames = [f.filename for f in request.files.values() if f]
    payload = {
        'property_id': property_id,
        'buyer': buyer,
        'amount': float(amount),
        'message': message,
        'filenames': filenames
    }
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))

    if private_key:
        # legacy check: private key corresponds to buyer
        if derive_public_from_private(private_key) != buyer:
            return jsonify({'error': 'Invalid privateKey for buyer'}), 403
    else:
        if not signature or not verify_demo_signature(buyer, payload_str, signature):
            return jsonify({'error': 'Invalid or missing signature for buyer'}), 403

    # Verify signature or legacy privateKey for buyer
    signature = request.form.get('signature') or request.form.get('sig')
    private_key = request.form.get('privateKey') or request.form.get('private_key')
    # Build canonical payload
    filenames = [f.filename for f in request.files.values() if f]
    payload = {'property_id': property_id, 'buyer': buyer, 'amount': float(amount), 'message': message, 'filenames': filenames}
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))

    verified = False
    if private_key:
        if derive_public_from_private(private_key) != buyer:
            return jsonify({'error': 'Invalid privateKey for buyer'}), 403
        verified = True
    else:
        if not signature or not verify_demo_signature(buyer, payload_str, signature):
            return jsonify({'error': 'Invalid or missing signature for buyer'}), 403
        verified = True

    # Ensure property exists and is available (not sold)
    prop_tx = None
    for block in reversed(blockchain.chain):
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'property' and tx.get('id') == property_id:
                prop_tx = tx.copy()
    if not prop_tx:
        return jsonify({'error': 'Property not found'}), 404

    # Apply subsequent updates/transfers to determine latest status
    latest_prop = prop_tx.copy()
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'property_update' and tx.get('property_id') == property_id:
                updates = tx.get('updates', {})
                latest_prop.update(updates)
            if tx.get('type') == 'property_transfer' and tx.get('property_id') == property_id:
                latest_prop['owner_public_key'] = tx.get('to')
                latest_prop['status'] = 'sold'

    if latest_prop.get('status') == 'sold':
        return jsonify({'error': 'Property already sold'}), 400

    request_id = str(uuid.uuid4())
    req_dir = os.path.join(PROPERTY_UPLOADS, property_id, 'requests', request_id)
    os.makedirs(req_dir, exist_ok=True)

    saved_files = []
    for key in request.files:
        f = request.files[key]
        if f:
            filename = f'{request_id}_{int(time.time())}_{f.filename}'
            path = os.path.join(req_dir, filename)
            f.save(path)
            # compute hash
            try:
                file_hash = getattr(blockchain, 'hash_file', compute_file_hash)(path)
            except Exception:
                file_hash = compute_file_hash(path)
            saved_files.append({'field': key, 'filename': filename, 'hash': file_hash})

    purchase_request = {
        'type': 'purchase_request',
        'request_id': request_id,
        'property_id': property_id,
        'buyer_public_key': buyer,
        'amount': float(amount),
        'message': message,
        'files': saved_files,
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'status': 'pending',
        'gas': GAS_FEE
    }

    miner = get_random_miner()
    blockchain.mine_block(purchase_request, miner_address=miner)
    return jsonify({'status': 'success', 'request_id': request_id}), 201


@app.route('/api/properties/<property_id>/requests', methods=['GET'])
def list_property_requests(property_id):
    """List purchase requests for a property."""
    requests_list = []
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'purchase_request' and tx.get('property_id') == property_id:
                requests_list.append(tx)
    return jsonify(requests_list)


@app.route('/api/owners/<owner_address>/requests', methods=['GET'])
def list_owner_requests(owner_address):
    """List incoming purchase requests for properties owned by owner_address."""
    owner_props = set()
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'property' and tx.get('owner_public_key') == owner_address:
                owner_props.add(tx.get('id'))

    incoming = []
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'purchase_request' and tx.get('property_id') in owner_props:
                incoming.append(tx)
    return jsonify(incoming)


@app.route('/api/properties/<property_id>/requests/<request_id>/approve', methods=['POST'])
def approve_request(property_id, request_id):
    """Owner approves a purchase request; creates a pending transaction."""
    data = request.json or {}
    owner = data.get('owner_public_key')
    if not owner:
        return jsonify({'error': 'owner_public_key is required'}), 400

    # Verify owner signature / privateKey
    signature = data.get('signature')
    private_key = data.get('privateKey')
    payload = {'property_id': property_id, 'request_id': request_id, 'owner': owner}
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    if private_key:
        if derive_public_from_private(private_key) != owner:
            return jsonify({'error': 'Invalid privateKey for owner'}), 403
    else:
        if not signature or not verify_demo_signature(owner, payload_str, signature):
            return jsonify({'error': 'Invalid or missing signature for owner'}), 403

    # Verify owner signature or legacy privateKey
    signature = data.get('signature')
    private_key = data.get('privateKey') or data.get('private_key')
    payload = {'property_id': property_id, 'request_id': request_id, 'owner': owner}
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))

    if private_key:
        if derive_public_from_private(private_key) != owner:
            return jsonify({'error': 'Invalid privateKey for owner'}), 403
    else:
        if not signature or not verify_demo_signature(owner, payload_str, signature):
            return jsonify({'error': 'Invalid or missing signature for owner'}), 403

    # Verify owner is actual owner of property
    prop_tx = None
    for block in reversed(blockchain.chain):
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'property' and tx.get('id') == property_id:
                prop_tx = tx
                break
        if prop_tx:
            break

    if not prop_tx:
        return jsonify({'error': 'Property not found'}), 404
    if prop_tx.get('owner_public_key') != owner:
        return jsonify({'error': 'Only owner can approve requests'}), 403

    # Find the purchase request
    purchase_req = None
    for block in reversed(blockchain.chain):
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'purchase_request' and tx.get('request_id') == request_id:
                purchase_req = tx
                break
        if purchase_req:
            break

    if not purchase_req:
        return jsonify({'error': 'Request not found'}), 404

    # Create a property transaction (pending)
    transaction_id = str(uuid.uuid4())
    tx_data = {
        'type': 'property_transaction',
        'id': transaction_id,
        'property_id': property_id,
        'buyer_public_key': purchase_req['buyer_public_key'],
        'seller_public_key': owner,
        'amount': purchase_req['amount'],
        'status': 'pending',
        'request_id': request_id,
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'gas': GAS_FEE
    }
    miner = get_random_miner()
    blockchain.mine_block(tx_data, miner_address=miner)

    # Mark purchase request as approved (mine update)
    approval_tx = {
        'type': 'purchase_request_update',
        'request_id': request_id,
        'status': 'approved',
        'transaction_id': transaction_id,
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'gas': GAS_FEE
    }
    blockchain.mine_block(approval_tx, miner_address=miner)

    return jsonify({'status': 'success', 'transaction_id': transaction_id}), 201


@app.route('/api/transactions/<transaction_id>/upload_docs', methods=['POST'])
def upload_transaction_docs(transaction_id):
    """Upload documents related to a transaction (buyer/seller exchange paperwork)."""
    # Accept multipart files
    # Find transaction
    tx = None
    for block in reversed(blockchain.chain):
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for t in transactions:
            if t.get('type') == 'property_transaction' and t.get('id') == transaction_id:
                tx = t
                break
        if tx:
            break

    if not tx:
        return jsonify({'error': 'Transaction not found'}), 404

    trans_dir = os.path.join(PROPERTY_UPLOADS, tx['property_id'], 'transactions', transaction_id)
    os.makedirs(trans_dir, exist_ok=True)
    saved = []
    for key in request.files:
        f = request.files[key]
        if f:
            filename = f'{transaction_id}_{int(time.time())}_{f.filename}'
            path = os.path.join(trans_dir, filename)
            f.save(path)
            try:
                file_hash = getattr(blockchain, 'hash_file', compute_file_hash)(path)
            except Exception:
                file_hash = compute_file_hash(path)
            saved.append({'field': key, 'filename': filename, 'hash': file_hash})

    doc_tx = {
        'type': 'transaction_documents',
        'transaction_id': transaction_id,
        'files': saved,
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'gas': GAS_FEE
    }
    miner = get_random_miner()
    blockchain.mine_block(doc_tx, miner_address=miner)
    return jsonify({'status': 'success', 'files': saved}), 201

@app.route("/api/transactions/user/<public_key>", methods=["GET"])
def get_user_property_transactions(public_key):
    """Get all property transactions for a user"""
    transactions = []
    for block in blockchain.chain:
        transactions_data = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions_data:
            if tx.get("type") == "property_transaction" and (
                tx.get("buyer_public_key") == public_key or 
                tx.get("seller_public_key") == public_key
            ):
                transactions.append(tx)
    return jsonify(transactions)

@app.route("/api/transactions/<transaction_id>/<action>", methods=["POST"])
def handle_property_transaction(transaction_id, action):
    """Handle property transaction confirmation or cancellation"""
    if action not in ["confirm", "cancel"]:
        return jsonify({"error": "Invalid action"}), 400

    data = request.json
    user_public_key = data.get("user_public_key")

    if not user_public_key:
        return jsonify({"error": "User public key is required"}), 400

    # Verify signature/privateKey for the acting user
    signature = data.get('signature')
    private_key = data.get('privateKey')
    payload = {'transaction_id': transaction_id, 'action': action, 'user_public_key': user_public_key}
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    if private_key:
        if derive_public_from_private(private_key) != user_public_key:
            return jsonify({'error': 'Invalid privateKey for user'}), 403
    else:
        if not signature or not verify_demo_signature(user_public_key, payload_str, signature):
            return jsonify({'error': 'Invalid or missing signature for user'}), 403

    # Find the transaction
    transaction = None
    for block in reversed(blockchain.chain):
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get("type") == "property_transaction" and tx.get("id") == transaction_id:
                transaction = tx
                break
        if transaction:
            break

    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    if action == "confirm":
        if user_public_key != transaction["seller_public_key"]:
            return jsonify({"error": "Only the seller can confirm the transaction"}), 403

        # Verify signature or legacy privateKey of the seller for confirmation
        signature = data.get('signature')
        private_key = data.get('privateKey') or data.get('private_key')
        payload = {'transaction_id': transaction_id, 'action': 'confirm', 'user_public_key': user_public_key}
        payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))

        if private_key:
            if derive_public_from_private(private_key) != user_public_key:
                return jsonify({'error': 'Invalid privateKey for seller'}), 403
        else:
            if not signature or not verify_demo_signature(user_public_key, payload_str, signature):
                return jsonify({'error': 'Invalid or missing signature for seller confirmation'}), 403

        # Transfer property ownership
        transfer_data = {
            "type": "property_transfer",
            "property_id": transaction["property_id"],
            "from": transaction["seller_public_key"],
            "to": transaction["buyer_public_key"],
            "amount": transaction["amount"],
            "transaction_id": transaction_id,
            "gas": GAS_FEE
        }
        
        miner = get_random_miner()
        blockchain.mine_block(transfer_data, miner_address=miner)
        # Also create a property_update record to reflect new owner and sold status
        property_update_tx = {
            'type': 'property_update',
            'property_id': transaction['property_id'],
            'owner_public_key': transaction['buyer_public_key'],
            'updates': {'owner_public_key': transaction['buyer_public_key'], 'status': 'sold'},
            'updated_at': datetime.datetime.utcnow().isoformat(),
            'gas': GAS_FEE
        }
        blockchain.mine_block(property_update_tx, miner_address=miner)

        # Update properties index if present (fast listing)
        try:
            props = _read_index(PROPERTIES_INDEX)
            changed = False
            for p in props:
                if p.get('id') == transaction['property_id']:
                    p['owner_public_key'] = transaction['buyer_public_key']
                    p['status'] = 'sold'
                    p['updated_at'] = property_update_tx['updated_at']
                    changed = True
                    break
            if changed:
                _write_index(PROPERTIES_INDEX, props)
        except Exception:
            pass

    # Update transaction status
    status_update = {
        "type": "property_transaction_update",
        "transaction_id": transaction_id,
        "status": "completed" if action == "confirm" else "cancelled",
    "timestamp": datetime.datetime.utcnow().isoformat(),
        "gas": GAS_FEE
    }
    
    miner = get_random_miner()
    blockchain.mine_block(status_update, miner_address=miner)

    return jsonify({"status": "success", "action": action})


@app.route('/api/properties/<property_id>', methods=['PUT'])
def update_property(property_id):
    """Update an existing property (owner only)"""
    data = request.json or {}
    owner_public_key = data.get('owner_public_key')
    if not owner_public_key:
        return jsonify({'error': 'owner_public_key is required to update property'}), 400

    # Find property
    property_tx = None
    for block in reversed(blockchain.chain):
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'property' and tx.get('id') == property_id:
                property_tx = tx
                break
        if property_tx:
            break

    if not property_tx:
        return jsonify({'error': 'Property not found'}), 404

    if property_tx.get('owner_public_key') != owner_public_key:
        return jsonify({'error': 'Only the owner can update the property'}), 403

    # Prepare update payload
    updates = {}
    for key in ['title', 'price', 'location', 'description']:
        if key in data:
            updates[key] = data[key]

    update_tx = {
        'type': 'property_update',
        'property_id': property_id,
        'owner_public_key': owner_public_key,
        'updates': updates,
        'updated_at': datetime.datetime.utcnow().isoformat(),
        'gas': GAS_FEE
    }

    miner = get_random_miner()
    blockchain.mine_block(update_tx, miner_address=miner)

    # Update properties index if present
    try:
        props = _read_index(PROPERTIES_INDEX)
        changed = False
        for p in props:
            if p.get('id') == property_id:
                p.update(updates)
                p['updated_at'] = update_tx['updated_at']
                changed = True
                break
        if changed:
            _write_index(PROPERTIES_INDEX, props)
    except Exception:
        pass

    return jsonify({'status': 'success', 'property_id': property_id})


@app.route('/api/properties/<property_id>/upload', methods=['POST'])
def upload_property_files(property_id):
    """Upload additional images or documents for an existing property.
    Multipart/form-data: owner_public_key, optional signature/privateKey, images (multiple), documents (multiple), remove_images (json array of filenames to remove)
    """
    owner = request.form.get('owner_public_key')
    if not owner:
        return jsonify({'error': 'owner_public_key is required'}), 400

    # Verify signature/privateKey similar to other endpoints
    signature = request.form.get('signature')
    private_key = request.form.get('privateKey') or request.form.get('private_key')
    payload_meta = {'property_id': property_id, 'owner': owner, 'filenames': [f.filename for f in request.files.values() if f]}
    payload_str = json.dumps(payload_meta, sort_keys=True, separators=(',', ':'))

    if private_key:
        if derive_public_from_private(private_key) != owner:
            return jsonify({'error': 'Invalid privateKey for owner'}), 403
    else:
        if not signature or not verify_demo_signature(owner, payload_str, signature):
            return jsonify({'error': 'Invalid or missing signature for owner'}), 403

    # Find the existing property and compute latest state
    prop_tx = None
    for block in reversed(blockchain.chain):
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'property' and tx.get('id') == property_id:
                prop_tx = tx.copy()
    if not prop_tx:
        return jsonify({'error': 'Property not found'}), 404

    # compute latest state
    latest_prop = prop_tx.copy()
    for block in blockchain.chain:
        transactions = block.data if isinstance(block.data, list) else [block.data]
        for tx in transactions:
            if tx.get('type') == 'property_update' and tx.get('property_id') == property_id:
                updates = tx.get('updates', {})
                latest_prop.update(updates)
            if tx.get('type') == 'property_transfer' and tx.get('property_id') == property_id:
                latest_prop['owner_public_key'] = tx.get('to')
                latest_prop['status'] = 'sold'

    if latest_prop.get('owner_public_key') != owner:
        return jsonify({'error': 'Only owner can upload files for this property'}), 403

    property_dir = os.path.join(PROPERTY_UPLOADS, property_id)
    os.makedirs(property_dir, exist_ok=True)

    # Handle removals (optional)
    remove_images = []
    try:
        rem = request.form.get('remove_images')
        if rem:
            remove_images = json.loads(rem)
    except Exception:
        remove_images = []

    # Read current images/documents lists
    current_images = list(latest_prop.get('images', []))
    current_documents = list(latest_prop.get('documents', []))

    # Remove requested images
    for fname in remove_images:
        # fname may be a full path like '/uploads/properties/<id>/file'
        try:
            if fname.startswith('/uploads'):
                rel = os.path.basename(fname)
            else:
                rel = fname
            filepath = os.path.join(property_dir, rel)
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass
        # remove from current_images
        current_images = [i for i in current_images if not i.endswith(rel)]

    saved_images = []
    saved_docs = []
    for key in request.files:
        f = request.files[key]
        if not f:
            continue
        filename = f"{uuid.uuid4()}_{f.filename}"
        path = os.path.join(property_dir, filename)
        f.save(path)
        web_path = f"/uploads/properties/{property_id}/{filename}"
        if key.lower().startswith('image') or key == 'images' or f.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            current_images.append(web_path)
            saved_images.append(web_path)
        else:
            # treat as document
            try:
                doc_hash = getattr(blockchain, 'hash_file', compute_file_hash)(path)
            except Exception:
                doc_hash = compute_file_hash(path)
            doc_entry = {'title': f.filename, 'hash': doc_hash, 'verified': False}
            current_documents.append(doc_entry)
            saved_docs.append(doc_entry)

    update_tx = {
        'type': 'property_update',
        'property_id': property_id,
        'owner_public_key': owner,
        'updates': {'images': current_images, 'documents': current_documents},
        'updated_at': datetime.datetime.utcnow().isoformat(),
        'gas': GAS_FEE
    }

    miner = get_random_miner()
    blockchain.mine_block(update_tx, miner_address=miner)

    # Update properties index if present
    try:
        props = _read_index(PROPERTIES_INDEX)
        changed = False
        for p in props:
            if p.get('id') == property_id:
                p['images'] = current_images
                p['documents'] = current_documents
                p['updated_at'] = update_tx['updated_at']
                changed = True
                break
        if changed:
            _write_index(PROPERTIES_INDEX, props)
    except Exception:
        pass

    return jsonify({'status': 'success', 'added_images': saved_images, 'added_documents': saved_docs, 'removed': remove_images}), 201

if __name__ == "__main__":
    app.run()
