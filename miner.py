# usage:
# ./miner.py <wallet> --node=<node>     # starts the mining for given node and the reward for given wallet

import hashlib
import argparse
import requests
import tools.pow as pow

def start(args):
    node_port = 5000 + int(args.node)
    node_address = f'http://127.0.0.1:{node_port}/blocks'
    res = requests.get(node_address)
    res_data = res.json()

    # check if theres any block to mine
    if len(res_data) == 0:
        print('There\'s no block to mine. check other nodes.')
        return

    # select the first block to mine
    block = res_data[0]
    print(f'selected block to mine: {block["id"]}')

    # add reward to block transactions
    # block["transactions"].append({
    #     'sender': f'node_{args.node}',
    #     'recipient': args.wallet,
    #     'amount': 1
    # })
    
    # start mining
    proof = pow.calc_proof(block)
    print(f'block mined with proof = {proof}');

    # send the mined block
    send_block_data = {
        'miner_wallet': args.wallet,
        'block_id': block["id"],
        'proof': proof,
    }
    send_block_res = requests.post(node_address, json=send_block_data)
    if send_block_res.status_code == 200:
        print('block mined successfully')
    else:
        print('block mined failed. server rejected mined block')

# cli parser
parser = argparse.ArgumentParser()
# transfer command parser
parser.add_argument('wallet')
parser.add_argument('--node', default='0')
parser.set_defaults(func=start)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
