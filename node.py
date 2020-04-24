import sys
from tools.blockchain import Blockchain
from flask import Flask, request, jsonify

bc = Blockchain()
app = Flask(__name__)
node_id = 0


@app.route('/transactions', methods=['POST'])
def transaction_add():
    values = request.get_json()
    bc.add_transaction(values['sender'], values['recipient'], values['amount'])
    res = { 'message': 'transaction added.' }
    return jsonify(res), 200

@app.route('/transactions', methods=['GET'])
def transactions_get():
    return jsonify(bc.transactions), 200

@app.route('/blocks', methods=['GET'])
def blocks_get():
    return jsonify(bc.blocks), 200


if __name__ == '__main__':
    node_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    node_port = 5000 + node_id
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
