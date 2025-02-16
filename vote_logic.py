import json
from time import time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.fernet import Fernet

encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

def generate_voter_key():
    """
    
    :return:
    """