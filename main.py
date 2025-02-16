from blockchain import Blockchain
from proof_of_work import proof_of_work
from vote_logic import add_vote
from time import time

blockchain = Blockchain()

difficulty = 4
target_time = 10 #time to get proof of work(in seconds)

def handle_vote():
    """
    handle the voting process by adding the votes to the blockchain.
    :return: does not return anything.
    """

    print(add_vote(blockchain, 'Voter1', 'CandidateA'))
    print(add_vote(blockchain, 'Voter2', 'CandidateC'))
    print(add_vote(blockchain, 'Voter1', 'CandidateB'))

def mine_block():
    global difficulty
    if hasattr(blockchain, 'current_votes') and blockchain.current_votes:
        #get previous block and its proof of work
        previous_block = blockchain.get_previous_block()
        previous_proof = previous_block['proof']
        start_time = time()

        print("Starting Proof of Work...")
        #generate new proof of work with dynamic difficulty
        new_proof = proof_of_work(previous_proof, difficulty)
        print(f"Proof of work found: {new_proof}")
        end_time = time()
        elapsed_time = end_time - start_time

        #adjust difficulty based on the time taken to get the proof of work of the current block
        if elapsed_time < target_time:
            difficulty += 1
        elif elapsed_time > target_time:
            difficulty = max(1, difficulty - 1)

        #create a new block with the valid proof of work
        previous_hash = blockchain.hash(previous_block)
        new_block = blockchain.create_block(new_proof, previous_hash)
        new_block['votes'] = blockchain.current_votes
        blockchain.current_votes = []

        print("New Block added to the blockchain with votes:", new_block)
    else:
        print("No new vote added to the blockchain.")

def main():
    print("Starting blockchain voting system...")
    handle_vote()

    print("\nMining Blocks...")
    mine_block()

if __name__ == '__main__':
    main()
