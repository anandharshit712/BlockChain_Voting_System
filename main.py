from blockchain import Blockchain
from proof_of_work import proof_of_work
from vote_logic import generate_voter_key, sign_voter, add_vote, count_vote
from time import time

blockchain = Blockchain()

difficulty = 5
valid_candidates = ["CandidateA", "CandidateB", "CandidateC"]

def handle_vote():
    """
    handle the voting process by adding the votes to the blockchain.
    """
    # Generate voter keys
    private_key, public_key = generate_voter_key()

    # Sign and add votes
    vote_data1 = {"voter_id": "Voter1", "candidate": "CandidateA"}
    signature1 = sign_voter(private_key, vote_data1)
    print(add_vote(blockchain, "Voter1", "CandidateA", valid_candidates, public_key, signature1))

    vote_data2 = {"voter_id": "Voter2", "candidate": "CandidateB"}
    signature2 = sign_voter(private_key, vote_data2)
    print(add_vote(blockchain, "Voter2", "CandidateB", valid_candidates, public_key, signature2))

    vote_data3 = {"voter_id": "Voter1", "candidate": "CandidateC"}
    signature3 = sign_voter(private_key, vote_data1)
    print(add_vote(blockchain, "Voter1", "CandidateC", valid_candidates, public_key, signature3))

def mine_block():
    """
    Mines a new block and stores the votes into the blockchain.
    """
    global difficulty
    if hasattr(blockchain, 'current_votes') and blockchain.current_votes:
        #get previous block and its proof of work
        previous_block = blockchain.get_previous_block()
        previous_proof = previous_block['proof']

        print("Starting Proof of Work...")
        #generate new proof of work with dynamic difficulty
        new_proof = proof_of_work(previous_proof, difficulty)
        print(f"Proof of work found: {new_proof}")

        # Hash the previous block
        previous_hash = blockchain.hash(previous_block)

        #create a new block with the valid proof of work
        new_block = blockchain.create_block(new_proof, previous_hash)
        new_block['votes'] = blockchain.current_votes
        blockchain.current_votes = []

        # print("New Block added to the blockchain with votes:", new_block)
    else:
        print("No new vote added to the blockchain.")

def display_results():
    """
    Display the vote counts for all candidates.
    """
    print("\nFinal vote counts:")
    vote_counts = count_vote(blockchain, valid_candidates)
    for candidate, count in vote_counts.items():
        print(f"{candidate}: {count} votes")

def main():
    print("Starting blockchain voting system...")
    handle_vote()

    print("\nMining Blocks...")
    mine_block()

    display_results()

if __name__ == '__main__':
    main()
