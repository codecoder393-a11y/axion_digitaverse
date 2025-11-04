
from flask import Flask, request, jsonify, abort, send_file
from axion_blockchain import Blockchain, generate_key_pair
from p2p import PeerNetwork
from file_storage import FileStorage
import sys
import threading
import os
import io

app = Flask(__name__)
blockchain = Blockchain()
peers = PeerNetwork()
file_storage = FileStorage(peers) 
users = {}  # {address: private_key}

@app.route("/api/create-user", methods=["POST"])
def create_user():
    data = request.json
    username = data["username"]
    public_key, private_key = generate_key_pair(username)
    blockchain.add_user(public_key)
    blockchain.mine_block({"type": "user", "username": username, "address": public_key}, miner_address=public_key)
    users[public_key] = private_key
    return jsonify({"publicKey": public_key, "privateKey": private_key})

def authenticate():
    address = request.headers.get("X-Address")
    token = request.headers.get("X-Token")
    if not address or not token or users.get(address) != token:
        abort(401, "Unauthorized")

@app.route("/api/wallet/<address>", methods=["GET"])
def get_wallet(address):
    authenticate()
    return jsonify({"address": address, "balance": blockchain.get_balance(address)})

@app.route("/api/transaction", methods=["POST"])
def transaction():
    authenticate()
    data = request.json
    tx = blockchain.create_transaction(data["from"], data["to"], int(data["amount"]))
    block = blockchain.mine_block(tx, miner_address=data["from"])
    peers.broadcast_chain(blockchain.to_dict())
    return jsonify({"block": block.to_dict()})

@app.route("/api/agent-deposit", methods=["POST"])
def agent_deposit():
    authenticate()
    data = request.json
    deposit_data = {
        "type": "agent_deposit",
        "from": data["agent_address"],
        "to": data["user_address"],
        "amount": int(data["amount"])
    }
    block = blockchain.mine_block(deposit_data, miner_address=data["agent_address"])
    peers.broadcast_chain(blockchain.to_dict())
    return jsonify({"block": block.to_dict()})

@app.route("/api/python-exec", methods=["POST"])
def python_exec():
    authenticate()
    import sys, io
    data = request.json
    code = data["code"]
    address = request.headers.get("X-Address")
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()
    try:
        exec(code, {})
        output = mystdout.getvalue()
    except Exception as e:
        output = str(e)
    finally:
        sys.stdout = old_stdout
    exec_data = {"type": "python_exec", "code": code, "output": output}
    block = blockchain.mine_block(exec_data, miner_address=address)
    peers.broadcast_chain(blockchain.to_dict())
    return jsonify({"output": output, "block": block.to_dict()})

@app.route("/api/chain", methods=["GET"])
def get_chain():
    return jsonify(blockchain.to_dict())

@app.route("/api/replace-chain", methods=["POST"])
def replace_chain():
    data = request.json
    blockchain.replace_chain(data["chain"])
    return jsonify({"message": "Chain replaced"})

@app.route("/api/add-peer", methods=["POST"])
def add_peer():
    data = request.json
    peers.add_peer(data["peer_url"])
    return jsonify({"message": "Peer added"})

@app.route("/api/store-file", methods=["POST"])
def store_file():
    authenticate()
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file temporarily
    file_path = os.path.join("backend/uploads", file.filename)
    file.save(file_path)

    # Split the file into chunks
    chunks = file_storage.split_file(file_path)
    
    # Store the chunks
    file_storage.store_chunks(chunks)
    
    # Get chunk hashes
    chunk_hashes = [chunk[0] for chunk in chunks]

    # Add a transaction to the blockchain
    address = request.headers.get("X-Address")
    file_data = {
        "type": "file_storage",
        "filename": file.filename,
        "chunk_hashes": chunk_hashes,
    }
    block = blockchain.mine_block(file_data, miner_address=address)
    peers.broadcast_chain(blockchain.to_dict())

    # Clean up the temporary file
    os.remove(file_path)

    return jsonify({"message": "File stored successfully", "block": block.to_dict()})


@app.route("/api/retrieve-file/<transaction_id>", methods=["GET"])
def retrieve_file(transaction_id):
    authenticate()
    
    # Find the transaction in the blockchain
    transaction = None
    for block in blockchain.chain:
        for tx in block.data:
            if tx.get('id') == transaction_id and tx.get('type') == 'file_storage':
                transaction = tx
                break
        if transaction:
            break
            
    if not transaction:
        return jsonify({"error": "File transaction not found"}), 404

    chunk_hashes = transaction['chunk_hashes']
    
    # Retrieve the file from chunks
    try:
        file_data = file_storage.retrieve_file(chunk_hashes)
        return send_file(
            io.BytesIO(file_data),
            mimetype='application/octet-stream',
            as_attachment=True,
            attachment_filename=transaction['filename']
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chunk/<chunk_hash>", methods=["GET"])
def get_chunk(chunk_hash):
    chunk_data = peers.chunks.get(chunk_hash)
    if chunk_data:
        return chunk_data
    else:
        abort(404)

@app.route("/api/chunk", methods=["POST"])
def receive_chunk():
    data = request.json
    chunk_hash = data.get('chunk_hash')
    chunk_data_hex = data.get('chunk_data')
    if chunk_hash and chunk_data_hex:
        chunk_data = bytes.fromhex(chunk_data_hex)
        peers.chunks[chunk_hash] = chunk_data
        return jsonify({"message": "Chunk received"})
    else:
        return jsonify({"error": "Invalid chunk data"}), 400

def sync_with_peers():
    import time
    while True:
        new_chain = peers.sync_chain(blockchain.to_dict())
        blockchain.replace_chain(new_chain)
        time.sleep(10)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 5000
    if len(sys.argv) > 2:
        for peer_url in sys.argv[2:]:
            peers.add_peer(peer_url)
    threading.Thread(target=sync_with_peers, daemon=True).start()
    app.run(port=port)
