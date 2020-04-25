# usage:
# client.py init                                                      # inits a new wallet
# client.py transfer <source_wallet> <destination_wallet> <amount>    # transfer amount to another wallet
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


# cli parser
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
# init command parser
init_parser = subparsers.add_parser('init')
init_parser.set_defaults(func=cmd_init)
# transfer command parser
transfer_parser = subparsers.add_parser('transfer')
transfer_parser.add_argument('src')
transfer_parser.add_argument('dst')
transfer_parser.add_argument('amount')
transfer_parser.set_defaults(func=cmd_transfer)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
