
import requests

class PeerNetwork:
    def __init__(self):
        self.peers = set()
        self.chunks = {}  # {chunk_hash: chunk_data}

    def add_peer(self, peer_url):
        self.peers.add(peer_url)

    def broadcast_chain(self, chain):
        for peer in self.peers:
            try:
                requests.post(f"{peer}/api/replace-chain", json={"chain": chain})
            except Exception:
                pass

    def sync_chain(self, local_chain):
        longest = local_chain
        for peer in self.peers:
            try:
                res = requests.get(f"{peer}/api/chain")
                peer_chain = res.json()
                if len(peer_chain) > len(longest):
                    longest = peer_chain
            except Exception:
                pass
        return longest

    def store_chunk(self, chunk_hash, chunk_data):
        """Stores a chunk locally and broadcasts it to the network."""
        self.chunks[chunk_hash] = chunk_data
        self.broadcast_chunk(chunk_hash, chunk_data)

    def get_chunk(self, chunk_hash):
        """Retrieves a chunk from the local cache or from peers."""
        if chunk_hash in self.chunks:
            return self.chunks[chunk_hash]
        
        for peer in self.peers:
            try:
                res = requests.get(f"{peer}/api/chunk/{chunk_hash}")
                if res.status_code == 200:
                    chunk_data = res.content
                    self.chunks[chunk_hash] = chunk_data  # Cache it
                    return chunk_data
            except Exception:
                pass
        return None

    def broadcast_chunk(self, chunk_hash, chunk_data):
        """Broadcasts a chunk to all peers on the network."""
        for peer in self.peers:
            try:
                requests.post(f"{peer}/api/chunk", json={'chunk_hash': chunk_hash, 'chunk_data': chunk_.hex()})
            except Exception:
                pass
