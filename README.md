# Blockchain example

## Environment
- Python 3.7
- Pipenv

## Contains
- simple Blockchain
- API server for manipulating Blockchain

## Run

### 環境構築
- `pipenv install`
- `pipenv shell`

### 鍵の作成
- `python generatekey.py`

### ブロックチェーンを起動
- `python main.py --ip <ip> --port <port> --key <key's path>`
- 自身のIPを認識するためにIPだけちゃんと指定してあげればOK

### ブロックチェーン操作
- index.htmlを開く
- my urlにserver.pyを起動したときのipをhttp://{ip}:{port}の形で指定する
- 情報の更新を行う
- ノードの追加、トランザクションの追加、マイニング、ブロックの同期などを行う

### 署名検証
- `python verify_signature.py`
- タイムスタンプとb64エンコードされた署名を指定


## API説明

### /uuid
- ユーザのuuidを返す

### /publickey
- ユーザの公開鍵を返す

### /transactions/new
- 新しいトランザクションを作成する

### /nodes
- ノード一覧を返す

### /nodes/register
- ノードの登録を行う

### /refresh
- 保持しているノードの情報を更新する
- 他のノードからノード情報をもらう

### /nodes/resolve
- ノード間でブロックのコンフリクトを解消する
- 最も長いブロックが適応される

### /mine
- マイニングを行う

### /chain
- 現在保持しているブロック一覧を返す