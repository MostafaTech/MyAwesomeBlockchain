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
    transaction = request.get_json()
    result = bc.add_transaction(transaction)
    if result[0] == False:
        return { 'message': result[1] }, 500
    return { 'message': 'transaction added.', 'transaction_id': result[1]["id"] }, 200

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

# returns all wallets
@app.route('/wallets', methods=['GET'])
def wallets_get_all():
    return jsonify(bc.wallets), 200

# returns wallet item and balance
@app.route('/wallets/<wallet_id>', methods=['GET'])
def wallets_get_item(wallet_id):
    item = bc.get_wallet_item(escape(wallet_id))
    return jsonify(item), 200

# adds a wallet
@app.route('/wallets', methods=['POST'])
def wallets_post():
    wallet = request.get_json()
    details = bc.add_wallet(wallet)
    return { 'message': 'wallet added to the collection' }, 200

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
