# coding: UTF-8

from typing import List
import hashlib
import json
from time import time
from uuid import uuid4
import requests
from urllib.parse import urlparse

class Block(object):
    def __init__(self, index: int, timestamp: float, transactions: List['Transaction'], proof: int, previous_hash: str):
        self._index = index
        self._timestamp = timestamp
        self._transactions = transactions
        self._proof = proof
        self._previous_hash = previous_hash

    @property
    def index(self):
        return self._index

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def transactions(self):
        return self._transactions
    @property
    def proof(self):
        return self._proof
    @property
    def previous_hash(self):
        return self._previous_hash

    def __iter__(self):
        yield ("_index", self._index)
        yield ("_timestamp", self._timestamp)
        yield ("_transactions", list(map(lambda t: t.__dict__, self._transactions)))
        yield ("_proof", self._proof)
        yield ("_previous_hash", self._previous_hash)

class Transaction(object):
    def __init__(self, sender: str, recipient: str, amount: int):
        self._sender = sender
        self._recipient = recipient
        self._amount = amount

    @property
    def sender(self):
        return self._sender

    @property
    def recipient(self):
        return self._recipient

    @property
    def amount(self):
        return self._amount

class Blockchain(object):
    def __init__(self):
        self._chain = []
        self._current_transactions = []
        self._nodes = {}
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof: int, previous_hash: str = None):
        block = Block (
            len(self._chain) + 1,
            time(),
            self._current_transactions,
            proof,
            previous_hash or self.hash(self._chain[-1])
        )
        self._current_transations = []
        self._chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, amount: int) -> int:
        self._current_transactions.append(
            Transaction(sender, recipient, amount)
        )
        return self.last_block.index + 1

    def register_node(self, address):
        parsed_url = urlparse(address)
        if len(parsed_url.netloc) < 1:
            raise Exception("URL is invalid!")
        response = requests.get(f'http://{parsed_url.netloc}/uuid')
        if response.status_code == 200:
            uuid = response.json()['uuid']
            self._nodes[parsed_url.netloc] = uuid
        else:
            raise Exception("GET uuid failed")

    @staticmethod
    def hash(block) -> str:
        block_string = json.dumps(dict(block), sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof) -> int:
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    def valid_chain(self, chain) -> bool:
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print('\n----------------\n')
            if block["_previous_hash"] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block.proof, block.proof):
                return False
            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True
        return False

    @staticmethod
    def valid_proof(last_proof: "Block", proof: int) -> bool:
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:5] == "00000"

    @property
    def last_block(self) -> 'Block':
        return self._chain[-1]

    @property
    def chain(self):
        return self._chain

    @property
    def nodes(self):
        return self._nodes
