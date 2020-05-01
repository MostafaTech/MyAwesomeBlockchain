import os
import shutil
import json
import base64
from uuid import uuid4
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

def generate(username):
    wallet_id = str(uuid4())
    # generate keys
    key_private = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    key_private_serialized = key_private.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()
    key_public = key_private.public_key()
    key_public_serialized = key_public.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    # finialy
    return {
        'id': wallet_id,
        'name': username,
        'private_key': key_private_serialized,
        'public_key': key_public_serialized
    }

def clear_files():
    if os.path.exists('wallets'):
        shutil.rmtree('wallets')

def store_in_file(wallet_object):
    # prepare file
    file_name = f'wallets/{wallet_object["name"]}'
    file_contents = f'{wallet_object["id"]}\n{wallet_object["private_key"]}{wallet_object["public_key"]}'
    # create wallets dir if it doesnt exists
    if not os.path.exists('wallets'):
        os.mkdir('wallets')
    # save the wallet file
    with open(file_name, "w") as f:
        f.write(file_contents)

def load_from_file(username):
    # check the file
    file_path = f'wallets/{username}'
    if not os.path.exists(file_path):
        print(f'no wallet found for {username}')
        return None
    # read file contents
    wid = ''
    private_key = ''
    with open(file_path, 'r') as f:
        file_lines = f.readlines()
        wid = file_lines[0][:-1]
        for i in range(1, 29):
            private_key += file_lines[i]
    # finaly
    return {
        'id': wid,
        'private_key': private_key
    }

def sign(private_key_serialized, data_object):
    # create private key object from serialized string
    private_key = serialization.load_pem_private_key(
        private_key_serialized.encode(),
        password=None, backend=default_backend()
    )
    # sign data_object with private key
    signature = private_key.sign(
        json.dumps(data_object, sort_keys=True).encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    # return base64-encoded string of signature
    return base64.b64encode(signature).decode()

def verify_signature(public_key_serialized, signature, data_object):
    public_key = serialization.load_pem_public_key(
        public_key_serialized.encode(),
        backend=default_backend()
    )
    try:
        public_key.verify(
            base64.b64decode(signature.encode()),
            json.dumps(data_object, sort_keys=True).encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256())
        return True
    except:
        return False
