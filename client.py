# usage:
# client.py init                                                      # inits a new wallet
# client.py transfer <source_wallet> <destination_wallet> <amount>    # transfer amount to another wallet
# client.py verify <transaction_id>                                   # checks if a transaction is verified
# client.py balance                                                   # calculate remaining of current wallet

from uuid import uuid4
import argparse
import requests


def cmd_init(args):
    wallet = uuid4()
    f = open("wallets.txt", "a+")
    f.write(f'{wallet}\n')
    f.close()
    print(f'wallet created: {wallet}')

def cmd_transfer(args):
    print(f'initiating transfer...')
    data = {
        'sender': args.src,
        'recipient': args.dst,
        'amount': args.amount
    }
    response = requests.post('http://127.0.0.1:5000/transactions', json=data)
    if response.status_code == 200:
        response_data = response.json()
        print(f'transfer finished sucessfully')
        print(f'transaction id: {response_data["transaction_id"]}')
    else:
        print(f'transfer finished with error: {response.status_code}')
        print(f'{response.text}')
        print(f'{data}')

def cmd_verify(args):
    print(f'verifying a transaction...')
    data = { 'transaction_id': args.transaction_id }
    response = requests.post('http://127.0.0.1:5000/verify/transaction', json=data)
    if response.status_code == 200:
        print('transaction successfully commited.')
    else:
        print('transaction is not commited yet or rejected.')

# cli parser
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
# init command parser
init_parser = subparsers.add_parser('init', help='Creates a new wallet')
init_parser.set_defaults(func=cmd_init)
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

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
