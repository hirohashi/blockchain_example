# coding: UTF-8

from typing import List
import hashlib
import json
from time import time
from uuid import uuid4
import requests
from urllib.parse import urlparse
import copy

class Block(object):
    def __init__(self, index: int, timestamp: float, transactions: List['Transaction'], proof: int, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.proof = proof
        self.previous_hash = previous_hash

    def __iter__(self):
        """
        transactionsの辞書を返すためにこれを作った
        """
        yield ("index", self.index)
        yield ("timestamp", self.timestamp)
        yield ("transactions", list(map(lambda t: t.__dict__, self.transactions)))
        yield ("proof", self.proof)
        yield ("previous_hash", self.previous_hash)

class Transaction(object):
    def __init__(self, sender: str, recipient: str, amount: int):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = {}
        self.new_block(previous_hash=1, proof=100)


    def new_block(self, proof: int, previous_hash: str = None):
        """
        新しいブロックを作成して追加する
        :param proof: int
        :previous_hash: 以前のハッシュ値
        """
        block = Block (
            len(self.chain) + 1,
            time(),
            self.current_transactions,
            proof,
            previous_hash or self.hash(self.chain[-1])
        )
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, amount: int) -> int:
        """
        新しいトランザクションを作成し追加する
        :param sender: int
        :param recipient: str
        :param amount: int
        :return: int 作成したトランザクションを含むブロックのアドレス
        """
        self.current_transactions.append(
            Transaction(sender, recipient, amount)
        )
        return self.last_block.index + 1

    def register_node(self, address):
        """
        ノードを追加する
        失敗したら例外を返す
        :param address
        """
        parsed_url = urlparse(address)
        self.nodes[parsed_url.netloc] = {}
        if len(parsed_url.netloc) < 1:
            raise Exception("URL is invalid!")
        # uuidを取得
        response = requests.get(f'http://{parsed_url.netloc}/uuid')
        if response.status_code == 200:
            uuid = response.json()['uuid']
            self.nodes[parsed_url.netloc]['uuid'] = uuid
        else:
            raise Exception("GET uuid failed")
        # publickeyを取得
        response = requests.get(f'http://{parsed_url.netloc}/publickey')
        if response.status_code == 200:
            key = response.json()['key']
            self.nodes[parsed_url.netloc]['key'] = key
        else:
            raise Exception("GET pubkey failed")

    @staticmethod
    def hash(block) -> str:
        block_string = json.dumps(dict(block), sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof: int) -> int:
        """
        PoWを行い，proofを返す
        :param last_proof: int 最後のブロックのproof
        :return:int 計算したproofの値
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    def valid_chain(self, chain: List["Block"]) -> bool:
        """
        ブロックチェーンが正しければtrue
        :param chain: List[Block]
        :return: bool
        """
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print('\n----------------\n')
            if block["previous_hash"] != self.hash(last_block):
                print('bad block: invalid previous hash')
                print(block["previous_hash"])
                return False
            if not self.valid_proof(last_block["proof"], block["proof"]):
                print('bad block: invalid proof')
                return False
            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        """
        他のノードとのコンフリクトを解消する
        """
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
            print(f'{chain}')
            self.chain = [
                Block(
                    chain["index"],
                    chain["timestamp"],
                    [Transaction(t["sender"], t["recipient"], t["amount"]) for t in chain["transactions"]],
                    chain["proof"],
                    chain["previous_hash"])
                for chain in new_chain]
            return True
        return False

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """
        proofの計算を行い，正しければtrueを返す
        :param last_proof: int
        :param proof: int
        :return bool
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:5] == "00000"

    @property
    def last_block(self) -> 'Block':
        return self.chain[-1]
