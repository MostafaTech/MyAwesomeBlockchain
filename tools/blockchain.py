from time import time
from uuid import uuid4
import json
import tools.pow as pow

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.blocks = []
        self.transactions = []
        self.node_id = 0
    
    def set_node(self, id):
        self.node_id = id

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
    
    def add_block_to_chain(self, block_id, proof, miner_wallet):
        mined_block = None
        for b in self.blocks:
            if b["id"] == block_id:
                mined_block = b
        if mined_block is not None:
            block_string = json.dumps(mined_block, sort_keys=True).encode()
            verified = pow.verify(block_string, proof)
            if verified:
                # add to chain
                self.chain.append(mined_block)
                # remove block from queue
                self.blocks.remove(mined_block)
                # add reward for the miner as a new transaction
                self.add_transaction(f'node_{self.node_id}', miner_wallet, 1)
            return verified
        return False

    def get_first_block(self):
        if (len(self.blocks) > 0):
            return self.blocks[0]
