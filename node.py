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
    return { 'message': result[1] }, 400

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


if __name__ == '__main__':
    node_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    node_port = 5000 + node_id
    bc.set_node(node_id)
    app.run(host='0.0.0.0', port=node_port)

# def print_transaction(tr):
#     print(f'{tr["sender"]} => {tr["recipient"]}\t{tr["amount"]}')

# bc = Blockchain()
# bc.add_transaction('mostafa', 'parisa', 10)
# bc.add_transaction('mostafa', 'parisa', 5)
# bc.add_transaction('parisa', 'mostafa', 15)

# print('queued blocks:')
# for b in bc.blocks:
#     for tr in b["transactions"]:
#         print_transaction(tr)

# print('queued transactions:')
# for tr in bc.transactions:
#     print_transaction(tr)
