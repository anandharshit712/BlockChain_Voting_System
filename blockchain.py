import hashlib
import json
from time import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')   # Initial Block also known as the Genesis Block

    def create_block(self, proof, previous_hash):
        """
        create a new block and then adding it to the blockchain

        :param proof: proof of work for the new block.
        :param previous_hash: the hash of the previous block in the chain .

        :return: a directory which contains the new block.
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.chain.append(block)
        return block

    def get_previous_block(self):
        """
        retrieve and then return the last block in the chain.
        :return: returns a directory which contains the last block of the chain.
        """
        return self.chain[-1]

    def hash(self, block):
        """
        create a hash digest of the block to ensure integrity.

        :param block: a directory which contains the block which is to be hashed.

        :return: returns a string which is the SHA-256 hash of the block.
        """
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()