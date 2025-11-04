import hashlib
import os
import json

def generate_key_pair(username=""):
    salt = os.urandom(16).hex()
    private_key = hashlib.sha256((username + salt).encode()).hexdigest()
    public_key = hashlib.sha256(private_key.encode()).hexdigest()
    return public_key, private_key

def calculate_hash(index, previous_hash, timestamp, data, nonce):
    value = str(index) + previous_hash + str(timestamp) + json.dumps(data, sort_keys=True) + str(nonce)
    return hashlib.sha256(value.encode()).hexdigest()