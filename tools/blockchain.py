from time import time
from uuid import uuid4
import requests
import tools.pow as pow

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.blocks = []
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

    def add_transaction(self, sender, recipient, amount):
        tr = {
            'id': str(uuid4()),
            'timestamp': time(),
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        self.transactions.append(tr)
        if (len(self.transactions) == 2):
            self.blocks.append({
                'id': str(uuid4()),
                'timestamp': time(),
                'transactions': self.transactions.copy()
            })
            self.transactions.clear()
        return tr
    
    def add_genesis_block_to_chain(self):
        block = { 'id': '0', 'timestamp': 0, 'transactions': [] }
        block["proof"] = pow.calc_proof(block)
        self.chain.append(block)
    
    def add_block_to_chain(self, block_id, proof, miner_wallet):
        # find the requested block in queue
        block = next((b for b in self.blocks if b["id"] == block_id), None)
        # check if the block is available
        if block is None:
            block = next((b for b in self.chain if b["id"] == block_id), None)
            if block is not None:
                return False, f'block is already in the chain with proof: {block["proof"]}'
            return False, 'block does not exists'
        
        verified = pow.verify(block, proof)
        if verified:
            # add to chain
            last_chain_block = self.chain[-1].copy()
            last_chain_block_proof = last_chain_block["proof"]
            del last_chain_block["proof"]
            last_chain_block_hash = pow.calc_hash_with_proof(last_chain_block, last_chain_block_proof)
            block["lastBlockHash"] = last_chain_block_hash
            block["proof"] = proof
            self.chain.append(block)
            # remove block from queue
            self.blocks.remove(block)
            # add reward for the miner as a new transaction
            self.add_transaction(f'node_{self.node_id}', miner_wallet, 1)
            # tell other nodes to add this block to their chain
            self._send_block_to_other_nodes(block)
            return True, 'block added to the chain'
        return False, 'can\'t verify requested block'

    def add_verified_block_to_chain(self, block):
        self.chain.append(block)

    def get_first_block(self):
        if (len(self.blocks) > 0):
            return self.blocks[0]

    def get_chain_transaction(self, transaction_id):
        for b in self.chain:
            for t in b["transactions"]:
                if t["id"] == transaction_id:
                    return t
        return None
    
    def get_balance(self, wallet_id):
        balance = 0
        for b in self.chain:
            for t in b["transactions"]:
                if t["recipient"] == wallet_id:
                    balance += int(t["amount"])
        return balance
    
    def _send_block_to_other_nodes(self, block):
        rejected_nodes = []
        for node in self.node_registery:
            result = requests.put(f'{node}/blocks', json=block)
            if result.status_code != 200:
                rejected_nodes.append(node)
