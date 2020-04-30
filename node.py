import sys
from markupsafe import escape
from flask import Flask, request, jsonify
from tools.blockchain import Blockchain
import tools.pow as pow

app = Flask(__name__)
node_id = 0

bc = Blockchain()
bc.add_genesis_block_to_chain()


# returns all memory transactions
@app.route('/transactions', methods=['GET'])
def transactions_get():
    return jsonify(bc.transactions), 200

# adds a transaction from a client
@app.route('/transactions', methods=['POST'])
def transactions_add():
    values = request.get_json()
    tr = bc.add_transaction(values['sender'], values['recipient'], values['amount'])
    res = { 'message': 'transaction added.', 'transaction_id': tr["id"] }
    return jsonify(res), 200

# verifies a transactions
@app.route('/transactions/<transaction_id>', methods=['GET'])
def transactions_verify(transaction_id):
    values = request.get_json()
    print(f'verifying: {escape(transaction_id)}')
    tr = bc.get_chain_transaction(escape(transaction_id))
    if tr is not None:
        return jsonify(tr), 200
    return { 'message': 'transaction does not exists' }, 404

# returns the chain
@app.route('/chain', methods=['GET'])
def chain_get():
    return jsonify(bc.chain), 200

# verifies and adds a block from other nodes
@app.route('/chain', methods=['POST'])
def chain_post():
    block = request.get_json()
    bc.add_block(block)
    return { 'message': 'block added to the chain' }, 200

# returns wallet data and balance
@app.route('/wallets/<wallet_id>', methods=['GET'])
def wallets_details(wallet_id):
    details = bc.get_wallet(escape(wallet_id))
    return jsonify(details), 200

# returns all registered nodes
@app.route('/registery', methods=['GET'])
def registery_get():
    return jsonify(bc.node_registery), 200

# adds a new node to registery
@app.route('/registery', methods=['POST'])
def registery_post():
    values = request.get_json()
    if bc.add_node(values['node_address']):
        return { 'message': 'node added to registery' }, 200
    return { 'message': 'failed to add node' }, 500


if __name__ == '__main__':
    node_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    node_port = 5000 + node_id
    bc.set_node(node_id)
    app.run(host='0.0.0.0', port=node_port)
