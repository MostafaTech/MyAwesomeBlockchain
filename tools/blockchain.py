from time import time
from uuid import uuid4
import threading
import requests
import tools.pow as pow
import tools.wallet as wallet

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.node_id = 0
        self.node_registery = []
        self.wallets = []
    
    def set_node(self, id):
        self.node_id = id
    
    def add_node(self, address):
        response = requests.get(f'{address}/chain')
        if response.status_code == 200:
            node_chain = response.json()
            if len(node_chain) > len(self.chain):
                self.chain = node_chain
            self.node_registery.append(address)
            print('[NODE] A node added successfully: ' + address)
            return True
        return False
    
    def add_genesis_block_to_chain(self):
        block = { 'id': '0', 'timestamp': 0, 'transactions': [] }
        block["proof"] = pow.calc_proof(block)
        self.chain.append(block)

    def add_transaction(self, transaction):
        # verify transaction
        sender_wallet = next((w for w in self.wallets if w["name"] == transaction["sender"]), None)
        if sender_wallet is None:
            return False, 'sender not found'
        transaction_without_signature = transaction.copy()
        del transaction_without_signature["signature"]
        if not wallet.verify_signature(sender_wallet["public_key"], transaction["signature"], transaction_without_signature):
            return False, 'signature verification failed'
        # find recipient wallet
        recipient_wallet = next((w for w in self.wallets if w["name"] == transaction["recipient"]), None)
        if recipient_wallet is None:
            return False, 'recipient not found'
        # create and append the transaction
        tr = {
            'id': str(uuid4()),
            'timestamp': time(),
            'signature': transaction["signature"],
            'sender': transaction["sender"],
            'recipient': transaction["recipient"],
            'amount': int(transaction["amount"])
        }
        self.transactions.append(tr)
        # mine a block if its time to mine (in another thread)
        if (len(self.transactions) == 2):
            thread = threading.Thread(target=self.mine, args=())
            thread.start()
        # finaly
        print('[NODE] A transaction added with id: ' + tr["id"])
        return True, tr
    
    def mine(self):
        print('[NODE] Mining started')
        # calculate last block has
        last_block = self.chain[-1].copy()
        last_block_proof = last_block["proof"]
        del last_block["proof"]
        last_block_hash = pow.calc_hash_with_proof(last_block, last_block_proof)
        # prepare transactions and add reward
        transactions = self.transactions.copy()
        transactions.append({
            'id': str(uuid4()),
            'timestamp': time(),
            'sender': '',
            'recipient': f'node_{self.node_id}',
            'amount': 10
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
        print('[NODE] Mining finished successfully')
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
            print('[NODE] A block imported successfully.')
            return True, 'block added to the chain'
        print('[NODE] Failed to import given block. verification failed.')
        return False, 'can\'t verify requested block'

    def get_chain_transaction(self, transaction_id):
        for b in self.chain:
            for t in b["transactions"]:
                if t["id"] == transaction_id:
                    return t
        return None
    
    def get_wallet_item(self, wallet_id):
        balance = 0
        for b in self.chain:
            for t in b["transactions"]:
                if t["recipient"] == wallet_id:
                    balance += t["amount"]
        return {
            'id': wallet_id,
            'balance': balance
        }

    def add_wallet(self, wallet):
        self.wallets.append(wallet)

    def _send_block_to_other_nodes(self, block):
        rejected_nodes = []
        for node in self.node_registery:
            result = requests.post(f'{node}/chain', json=block)
            if result.status_code != 200:
                rejected_nodes.append(node)
        # feedback
        rejected_nodes_msg = ''
        if len(rejected_nodes) > 0:
            rejected_nodes_msg = f' ({len(rejected_nodes)} failed)'
        print(f'[NODE] Sending block to other nodes finished.{rejected_nodes_msg}')
