from time import time
from uuid import uuid4
import requests
import tools.pow as pow

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.node_id = 0
        self.node_registery = []
    
    def set_node(self, id):
        self.node_id = id
    
    def add_node(self, address):
        response = requests.get(f'{address}/chain')
        if response.status_code == 200:
            node_chain = response.json()
            if len(node_chain) > len(self.chain):
                self.chain = node_chain
            self.node_registery.append(address)
            return True
        return False
    
    def add_genesis_block_to_chain(self):
        block = { 'id': '0', 'timestamp': 0, 'transactions': [] }
        block["proof"] = pow.calc_proof(block)
        self.chain.append(block)

    def add_transaction(self, sender, recipient, amount):
        # create and append the transaction
        tr = {
            'id': str(uuid4()),
            'timestamp': time(),
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        self.transactions.append(tr)
        # mine a block if its time to mine
        if (len(self.transactions) == 2):
            self.mine()
        # finaly
        return tr
    
    def mine(self):
        # calculate last block has
        last_block = self.chain[-1].copy()
        last_block_proof = last_block["proof"]
        del last_block["proof"]
        last_block_hash = pow.calc_hash_with_proof(last_block, last_block_proof)
        # prepare transactions and add wage
        transactions = self.transactions.copy()
        transactions.append({
            'id': str(uuid4()),
            'timestamp': time(),
            'sender': '',
            'recipient': f'node_{self.node_id}',
            'amount': 1
        })
        # create the block
        block = {
            'last_block_hash': last_block_hash,
            'transactions': transactions
        }
        # calculate the proof
        proof = pow.calc_proof(block)
        block['proof'] = proof
        # append block to the chain
        self.chain.append(block)
        # remove block transactions from memory
        for btr in transactions:
            for mtr in self.transactions:
                if mtr["id"] == btr["id"]:
                    self.transactions.remove(mtr)
        # tell other nodes to add this block to their chain
        self._send_block_to_other_nodes(block)

    def add_block(self, block):
        # verify block
        block_to_verify = {
            'last_block_hash': block["last_block_hash"],
            'transactions': block["transactions"]
        }
        verified = pow.verify(block_to_verify, block["proof"])
        # add to the chain
        if verified:
            self.chain.append(block)
            return True, 'block added to the chain'
        return False, 'can\'t verify requested block'

    def get_chain_transaction(self, transaction_id):
        for b in self.chain:
            for t in b["transactions"]:
                if t["id"] == transaction_id:
                    return t
        return None
    
    def get_wallet(self, wallet_id):
        balance = 0
        for b in self.chain:
            for t in b["transactions"]:
                if t["recipient"] == wallet_id:
                    balance += int(t["amount"])
        return {
            'id': wallet_id,
            'balance': balance
        }
    
        rejected_nodes = []
        for node in self.node_registery:
            result = requests.put(f'{node}/transaction', json=transaction)
            if result.status_code != 200:
                rejected_nodes.append(node)

    def _send_block_to_other_nodes(self, block):
        rejected_nodes = []
        for node in self.node_registery:
            result = requests.post(f'{node}/chain', json=block)
            if result.status_code != 200:
                rejected_nodes.append(node)
