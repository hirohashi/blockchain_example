import copy
import json
import argparse
from textwrap import dedent
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request
import requests
from base64 import b64decode, b64encode
from flask_cors import CORS
from blockchain import Blockchain
from util import sign

parser = argparse.ArgumentParser(description="blockchain example")
parser.add_argument('--ip', type=str, default="0.0.0.0")
parser.add_argument('--port', type=int, default=5000)
parser.add_argument('--key', type=str, default="key.pem")
args = parser.parse_args()

app = Flask(__name__)
# CORSを許可する
CORS(app)
node_identifier = str(uuid4()).replace('-', '')

privatekey = open(args.key).read()
publickey = open(args.key + '.pub').read()

blockchain = Blockchain()

@app.route('/uuid', methods=['GET'])
def getUuid():
    """
    GET /uuid
    uuidを取得する
    """
    return jsonify({'uuid': node_identifier}), 200

@app.route('/publickey', methods=['GET'])
def getpubkey():
    """
    GET /publickey
    公開鍵を取得する
    """
    return jsonify({'key': publickey}), 200

@app.route('/transactions/new', methods=['POST'])
def new_transactions():
    """
    !! このAPIは本人しか叩けないよ !!
    POST /transactions/new
    新しいトランザクションを追加する
    {'sender': value, 'recipient': value, 'amount': value}
    """
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    timestamp = time()
    signature = sign(privatekey, timestamp)
    index = blockchain.new_transaction(values['sender'], values['recipient'], int(values['amount']), timestamp, signature)
    # 他のノードへトランザクションを共有
    for node in blockchain.nodes:
        response = requests.post(f'http://{node}/transactions/new', json=values)
        if response.status_code != 200:
            return 'Cannot send transaction', 500
    result = {'message': f'transaction append {index} into block'}
    return jsonify(result), 200

@app.route('/nodes', methods=['GET'])
def get_nodes():
    """
    GET /nodes
    ノード一覧を取得する
    """
    return jsonify(blockchain.nodes), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    """
    POST /nodes/register
    新しいノードを登録する
    """
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "error: invalid node", 400
    for node in nodes:
        # 自分自身の場合はスキップ
        if f'{args.ip}:{args.port}' in node:
            continue
        try:
            blockchain.register_node(node)
        except Exception as err:
            print(err)
            return "error occured", 400
    response = {
        'message': 'new node registerd',
        'total_nodes': blockchain.nodes
    }
    return jsonify(response), 200

@app.route('/refresh', methods=['POST'])
def reflesh():
    """
    POST /refresh
    ノード情報を更新する
    """
    count = 0
    oldNode = copy.deepcopy(blockchain.nodes)
    for node in oldNode:
        response = requests.get(f'http://{node}/nodes')
        if response.status_code == 200:
            others = response.json()
            for other in others:
                if f'{args.ip}:{args.port}' in other:
                    continue
                try:
                    blockchain.register_node(f'http://{other}')
                    count += 1
                except Exception as err:
                    print(err)
                    return "error occured", 400
        else:
            return "cannot get other nodes", 500
    response = {
        'message': '%d nodes added' % count,
        'total_nodes': blockchain.nodes
    }
    return jsonify(response), 200


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    """
    GET /nodes/resolve
    ノード間のブロックチェーンのコンフリクトを解消する
    """
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'chain replaced',
            'new_chain': list(map(lambda c: dict(c), blockchain.chain))
        }
    else:
        response = {
            'message': 'chain consensused',
            'chain': list(map(lambda c: dict(c), blockchain.chain))
        }
    return jsonify(response), 200

@app.route('/mine', methods=['GET'])
def mine():
    """
    GET /mine
    マイニングをする
    """
    last_block = blockchain.last_block
    last_proof = last_block.proof
    proof = blockchain.proof_of_work(last_proof)
    timestamp = time()
    signature = sign(privatekey, timestamp)
    blockchain.new_transaction(
        sender = "0",
        recipient = node_identifier,
        amount = 1,
        timestamp = timestamp,
        signature = signature
    )
    block = blockchain.new_block(proof)
    response = {
        'message': 'new block mining!!',
        'index': block.index,
        'transactions': list(map(lambda t: t.__dict__, block.transactions)),
        'proof': block.proof,
        'previous_hash': block.previous_hash,
    }
    print(response['transactions'])
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    """
    GET /chain
    ブロックチェーンを返す
    """
    response = {
        'chain': list(map(lambda c: dict(c), blockchain.chain)),
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

if __name__ == '__main__':
    print(node_identifier)
    app.run(host=args.ip, port=args.port)