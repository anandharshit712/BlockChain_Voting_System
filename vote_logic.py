import json
from time import time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.fernet import Fernet

encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

def generate_voter_key():
    """
    Generate RSA key for the voter.
    :return:
    - Private Key - the voter's Private key
    - public key - the voter's Public key
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key

def sign_voter(private_key, vote_data):
    """
    Signs a vote using the voter;s private key.

    :param private_key: The voter's private key.
    :param vote_data:  The voter's public key.
    :return: bytes: the signature.
    """
    vote_json = json.dumps(vote_data, sort_keys = True).encode()
    signature = private_key.sign(
        vote_json,
        padding.PSS(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return signature

def verify_vote(public_key, vote_data, signature):
    """
    Verifies a vote's signature using the voter's public key.

    :param public_key:(RSAPublicKey)The voter's public key.
    :param vote_data:(Dict) The vote data to verify.
    :param signature:(Bytes) The signature to verify.
    :return: (bool) True if the signature is valid, False otherwise.
    """
    voter_json = json.dumps(vote_data, sort_keys = True).encode()
    try:
        public_key.verify(
            signature,
            voter_json,
            padding.PSS(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False

def add_vote(blockchain, voter_id, candidate, valid_candidates, public_key, signature):
    """
    Add a new vote to the blockchain with the validation nad encryption.

    :param blockchain: (Blockchain) The blockchain instance.
    :param voter_id: (str) Unique ID of the voter.
    :param candidate: (str) Name of the candidate.
    :param valid_candidates: (list) List of valid candidates.
    :param public_key: (RSAPublicKey) The voter's public key.
    :param signature: (bytes) voter's signature.
    :return: (str) Voter's signature.
    """
    if candidate not in valid_candidates:
        return f"Invalid Candidate: {candidate}."
    vote_data = {"voter_id": voter_id, "candidate": candidate}
    if not verify_vote(public_key, vote_data, signature):
        return f"Invalid signature. Vote Rejected."
    for block in blockchain.chain:
        if 'votes' in block:
            for vote in block['votes']:
                if vote['voter_id'] -- voter_id:
                    return "Voter has already voted."
    encrypted_vote = cipher.encrypt(json.dumps(vote_data).encode())
    if not hasattr(blockchain, 'current_votes'):
        blockchain.current_votes = []
    blockchain.current_votes.append({
        'vote': encrypted_vote,
        'timestamp': time(),
    })
    return f"Vote Successfully added for {candidate} by the voter {voter_id}."

def count_vote(blockchain, valid_candidate):
    """
    Count the number of votes for each candidate.

    :param blockchain: (Blockchain) The blockchain instance.
    :param valid_candidate: (list) List of valid candidates.
    :return: (dict) Vote counts for each candidate.
    """
    vote_count = {candidate: 0 for candidate in valid_candidate}
    for block in blockchain.chain:
        if 'votes' in block:
            for vote_entry in block['votes']:
                decrypt_vote = json.loads(cipher.decrypt(vote_entry['vote']).decode())
                candidate = decrypt_vote['candidate']
                if candidate in valid_candidate:
                    vote_count[candidate] += 1
    return vote_count
