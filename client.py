# usage:
# client.py init <name>                                                         # inits a new wallet for username
# client.py clear                                                               # removes all wallets
# client.py [--node=<node_id=0>] transfer <src_wallet> <dst_wallet> <amount>    # transfer amount to another wallet
# client.py [--node=<node_id=0>] verify <transaction_id>                        # checks if a transaction is verified
# client.py [--node=<node_id=0>] balance                                        # calculate remaining of current wallet

import argparse
import requests
import tools.wallet as wallet

node_url = 'http://127.0.0.1:5000'
def set_node(node_id):
    node_port = 5000 + int(node_id)
    node_url = f'http://127.0.0.1:{node_port}'

def cmd_init(args):
    # generate a wallet and save it in a file
    w = wallet.generate(args.name)
    wallet.store_in_file(w)
    # send wallet to a node
    wallet_json = {
        'id': w["id"],
        'name': w["name"],
        'public_key': w["public_key"]
    }
    response = requests.post(f'{node_url}/wallets', json=wallet_json)
    if response.status_code == 200:
        print(f'wallet created successfully')
    else:
        print('failed to create new wallet')

def cmd_clear(args):
    wallet.clear_files()

def cmd_transfer(args):
    set_node(args.node)
    # prepare transaction data
    data = {
        'sender': args.src,
        'recipient': args.dst,
        'amount': args.amount
    }
    # sign transaction
    w = wallet.load_from_file(args.src)
    data["signature"] = wallet.sign(w['private_key'], data)
    # send to a node
    response = requests.post(f'{node_url}/transactions', json=data)
    if response.status_code == 200:
        response_data = response.json()
        print(f'transaction id: {response_data["transaction_id"]}')
    else:
        response_data = response.json()
        print(f'transfer failed: {response_data["message"]}')

def cmd_verify(args):
    set_node(args.node)
    response = requests.get(f'{node_url}/transactions/{args.transaction_id}')
    if response.status_code == 200:
        print('transaction successfully commited.')
    else:
        print('transaction is not commited yet or rejected.')

def cmd_balance(args):
    set_node(args.node)
    response = requests.get(f'{node_url}/wallets/{args.wallet_id}')
    if response.status_code == 200:
        response_data = response.json()
        print(f'balance: {response_data["balance"]}')
    else:
        print('Theres an error calculating the balance of this wallet.')


# cli parser
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
parser.add_argument('--node', default='0')
# init command parser
init_parser = subparsers.add_parser('init', help='Creates a new wallet')
init_parser.add_argument('name', help='Wallet user name')
init_parser.set_defaults(func=cmd_init)
# clear command parser
clear_parser = subparsers.add_parser('clear', help='Removes all wallets')
clear_parser.set_defaults(func=cmd_clear)
# transfer command parser
transfer_parser = subparsers.add_parser('transfer', help='Transfer an amount from one wallet to another')
transfer_parser.add_argument('src', help='Source wallet')
transfer_parser.add_argument('dst', help='Destination wallet')
transfer_parser.add_argument('amount', help='Amount to transfer')
transfer_parser.set_defaults(func=cmd_transfer)
# verify command parser
verify_parser = subparsers.add_parser('verify', help='Verifies a transfer')
verify_parser.add_argument('transaction_id', help='Transaction id to verify')
verify_parser.set_defaults(func=cmd_verify)
# balance command parser
balance_parser = subparsers.add_parser('balance', help='Calculates the balance of a wallet')
balance_parser.add_argument('wallet_id', help='Wallet id to calculate')
balance_parser.set_defaults(func=cmd_balance)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
