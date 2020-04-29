import sys
from flask import Flask, request, jsonify
from tools.blockchain import Blockchain
import tools.pow as pow

app = Flask(__name__)
node_id = 0

bc = Blockchain()
bc.add_genesis_block_to_chain()


@app.route('/transactions', methods=['POST'])
def transaction_add():
    values = request.get_json()
    tr = bc.add_transaction(values['sender'], values['recipient'], values['amount'])
    res = { 'message': 'transaction added.', 'transaction_id': tr["id"] }
    return jsonify(res), 200

@app.route('/transactions', methods=['GET'])
def transactions_get():
    return jsonify(bc.transactions), 200

@app.route('/blocks', methods=['GET'])
def blocks_get():
    return jsonify(bc.blocks), 200

@app.route('/blocks', methods=['POST'])
def blocks_post():
    values = request.get_json()
    result = bc.add_block_to_chain(values['block_id'], values['proof'], values['miner_wallet'])
    if result[0]:
        return { 'message': result[1] }, 200
    return { 'message': result[1] }, 500

@app.route('/blocks', methods=['PUT'])
def blocks_put():
    block = request.get_json()
    bc.add_verified_block_to_chain(block)
    return { 'message': 'block added to the chain' }, 200

@app.route('/chain', methods=['GET'])
def chain_get():
    return jsonify(bc.chain), 200

@app.route('/verify/transaction', methods=['POST'])
def verify_transaction():
    values = request.get_json()
    tr = bc.get_chain_transaction(values['transaction_id'])
    if tr is not None:
        return jsonify(tr), 200
    return { 'message': 'transaction does not exists' }, 404

@app.route('/wallet/balance', methods=['POST'])
def wallet_balance():
    values = request.get_json()
    balance = bc.get_balance(values['wallet_id'])
    return { 'balance': balance }, 200

@app.route('/registery', methods=['GET'])
def registery_get():
    return jsonify(bc.node_registery), 200

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
