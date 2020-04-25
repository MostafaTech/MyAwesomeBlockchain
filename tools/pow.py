import hashlib

def calc_proof(source):
    proof = 0
    found = False
    guess_hash = ''
    while found is False:
        guess = f'{source}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        if (guess_hash[:4] == '0000'):
            found = True
        else:
            proof += 1
    return proof

def verify(source, proof):
    guess = f'{source}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    if guess_hash[:4] == '0000':
        return True
    return False