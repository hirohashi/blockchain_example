import argparse
from textwrap import dedent
from uuid import uuid4
from flask import Flask, jsonify, request
from flask_cors import CORS
from blockchain import Blockchain

parser = argparse.ArgumentParser(description="blockchain example")
parser.add_argument('--port', type=int, default=5000)
parser.add_argument('--key', type=str, default="blockchain_rsa")
args = parser.parse_args()

app = Flask(__name__)
CORS(app)
node_identifier = str(uuid4()).replace('-', '')

privatekey = open(args.key).read()
publickey = open(args.key + '.pub').read()

blockchain = Blockchain()

@app.route('/uuid', methods=['GET'])
def getUuid():
    return jsonify({'uuid': node_identifier}), 200

@app.route('/publickey', methods=['GET'])
def getpubkey():
    return jsonify({'key': publickey}), 200

@app.route('/transactions/new', methods=['POST'])
def new_transactions():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    index = blockchain.new_transaction(values['sender'], values['recipient'], int(values['amount']))
    response = {'message': f'transaction append {index} into block'}
    return jsonify(response), 200

@app.route('/nodes', methods=['GET'])
def get_nodes():
    return jsonify(blockchain.nodes), 200

@app.route('/nodes/register', methods=['POST'])
def register_node():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "error: invalid node", 400
    for node in nodes:
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

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
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
    last_block = blockchain.last_block
    last_proof = last_block.proof
    proof = blockchain.proof_of_work(last_proof)
    blockchain.new_transaction(
        sender = "0",
        recipient = node_identifier,
        amount = 1,
    )
    block = blockchain.new_block(proof)
    response = {
        'message': 'new block mining!!',
        'index': block.index,
        'transactions': list(map(lambda t: t.__dict__, block.transactions)),
        'proof': block.proof,
        'previous_hash': block.previous_hash,
    }
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': list(map(lambda c: dict(c), blockchain.chain)),
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

if __name__ == '__main__':
    print(node_identifier)
    app.run(host='0.0.0.0', port=args.port)
