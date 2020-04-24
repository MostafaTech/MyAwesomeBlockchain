# MyAwesomeBlockchain
This is a simple implemention of a blockchain with python

### Use the program

To start a server node
```
$ python ./node.py <node_id>
----------------------------
$ python ./node.py 1
 * Serving Flask app "node" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:5001/ (Press CTRL+C to quit)
```

Create wallets (create at least 3 wallets for sender, recipient and miner)
```
$ python ./client.py init
wallet created: 33ea7a7c-5f20-4ebd-9d62-313a0e298836

$ python ./client.py init
wallet created: 7cfc3ceb-78df-4898-b327-cc3abfae1c50

$ python ./client.py init
wallet created: 3cc8aa7a-2370-4c84-bdfa-d22cda041403
```

transfer some money (at least two transfers to create one block)
```
$ python ./client.py transfer <sender_wallet> <recipient_wallet> <amount>
---------------------------------------------
$ python ./client.py transfer 33ea7a7c-5f20-4ebd-9d62-313a0e298836 7cfc3ceb-78df-4898-b327-cc3abfae1c50 100
initiating transfer...
transfer finished sucessfully

$ python ./client.py transfer 33ea7a7c-5f20-4ebd-9d62-313a0e298836 7cfc3ceb-78df-4898-b327-cc3abfae1c50 200
initiating transfer...
transfer finished sucessfully
```

to seed blocks send a GET request same as below
```
GET 127.0.0.1:5001/blocks
-------------------------
[
    {
        "id": "6b44a4c1-669a-42ed-a30d-8d107a4a3885",
        "timestamp": 1587756259.944004,
        "transactions": [
            {
                "amount": "100",
                "recipient": "7cfc3ceb-78df-4898-b327-cc3abfae1c50",
                "sender": "33ea7a7c-5f20-4ebd-9d62-313a0e298836"
            },
            {
                "amount": "200",
                "recipient": "7cfc3ceb-78df-4898-b327-cc3abfae1c50",
                "sender": "33ea7a7c-5f20-4ebd-9d62-313a0e298836"
            }
        ]
    }
]
```

Let's mine the blocks
```
$ python ./miner.py <miner_wallet> --node=<node_id>
--------------------------------------------
$ python ./miner.py 3cc8aa7a-2370-4c84-bdfa-d22cda041403 --node=1
selected block to mine: 6b44a4c1-669a-42ed-a30d-8d107a4a3885
block mined with proof = 35416
```
