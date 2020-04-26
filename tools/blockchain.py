from time import time
from uuid import uuid4
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
    
    def add_genesis_block_to_chain(self):
        block = { 'id': '0', 'timestamp': 0, 'transactions': [] }
        block["proof"] = pow.calc_proof(block)
        self.chain.append(block)
    
    def add_block_to_chain(self, block_id, proof, miner_wallet):
        # check if the block is available
        block_is_in_queue = len(list(b for b in self.blocks if b["id"] == block_id)) > 0
        if not block_is_in_queue:
            block_is_in_chain = len(list(b for b in self.chain if b["id"] == block_id)) > 0
            if block_is_in_chain:
                block_in_chain = next(b for b in self.chain if b["id"] == block_id)
                return False, f'block is already in chain with proof: {block_in_chain["proof"]}'
            return False, 'block does not exists'

        mined_block = next(b for b in self.blocks if b["id"] == block_id)
        if mined_block is not None:
            verified = pow.verify(mined_block, proof)
            if verified:
                # add to chain
                last_chain_block = self.chain[-1].copy()
                last_chain_block_proof = last_chain_block["proof"]
                del last_chain_block["proof"]
                last_chain_block_hash = pow.calc_hash_with_proof(last_chain_block, last_chain_block_proof)
                mined_block["lastBlockHash"] = last_chain_block_hash
                mined_block["proof"] = proof
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
