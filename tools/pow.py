import json
import hashlib

def calc_proof(source):
    proof = 0
    found = False
    guess_hash = ''
    source_serialized = serialize(source)
    while found is False:
        guess = f'{source_serialized}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        if (guess_hash[:4] == '0000'):
            found = True
        else:
            proof += 1
    return proof

def calc_hash_with_proof(source, proof):
    source_serialized = serialize(source)
    guess = f'{source_serialized}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash

def verify(source, proof):
    guess_hash = calc_hash_with_proof(source, proof)
    if guess_hash[:4] == '0000':
        return True
    return False

def serialize(source):
    return json.dumps(source, sort_keys=True).encode()
