
import hashlib
import os

class FileStorage:
    def __init__(self, node):
        self.node = node
        self.chunk_size = 1024 * 1024  # 1MB

    def split_file(self, file_path):
        """Splits a file into chunks."""
        chunks = []
        with open(file_path, 'rb') as f:
            while True:
                chunk_data = f.read(self.chunk_size)
                if not chunk_data:
                    break
                chunk_hash = hashlib.sha256(chunk_data).hexdigest()
                chunks.append((chunk_hash, chunk_data))
        return chunks

    def store_chunks(self, chunks):
        """Stores chunks on the network."""
        for chunk_hash, chunk_data in chunks:
            # In a real implementation, this would involve finding nodes on the network
            # and sending them the chunks to store. For now, we'll just store them locally.
            self.node.store_chunk(chunk_hash, chunk_data)

    def retrieve_file(self, chunk_hashes):
        """Retrieves a file from the network by its chunk hashes."""
        file_data = b''
        for chunk_hash in chunk_hashes:
            chunk_data = self.node.get_chunk(chunk_hash)
            if chunk_data is None:
                raise Exception(f"Chunk with hash {chunk_hash} not found.")
            file_data += chunk_data
        return file_data
