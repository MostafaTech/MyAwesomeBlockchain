from time import time
from uuid import uuid4

class Blockchain(object):
    def __init__(self):
        self.blocks = []
        self.transactions = []

    def add_transaction(self, sender, recipient, amount):
        self.transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        if (len(self.transactions) == 2):
            self.blocks.append({
                'id': uuid4(),
                'timestamp': time(),
                'transactions': self.transactions.copy()
            })
            self.transactions.clear()
    
    def get_first_block(self):
        if (len(self.blocks) > 0):
            return self.blocks[0]
