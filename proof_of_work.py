import hashlib

def proof_of_work(previous_proof, difficulty):
    """
    Performs a proof of work on the given difficulty then returns the new proof of work of the block.

    :param previous_proof: the proof of work of the previous block.
    :param difficulty: The current level of difficulty for calculating the proof of work.(The number of leading zeros required to be a valid proof of work.)
    :return: Returns a valid proof of work for the current block for the given difficulty level.
    """
    new_proof = 1
    check_proof = False
    target = '0' * difficulty

    while not check_proof:
        hash_method = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
        if hash_method[:difficulty] == target:
            check_proof = True
        else:
            new_proof += 1
    return new_proof