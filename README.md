# Blockchain example

## Environment
- Python 3.7
- Pipenv

## Contains
- simple Blockchain
- API server for manipulating Blockchain

## Run
- `pipenv shell`
- `python main.py -p <port>`


### New Transactions

```
curl -X POST -H "Content-Type: application/json" -d '{
 "sender": "d4ee26eee15148ee92c6cd394edd974e",
 "recipient": "someone-other-address",
 "amount": 5
}' "http://{hostname}/transactions/new"
```

### Register node

```
curl -X POST -H "Content-Type: application/json" -d '{
    "nodes": ["http://localhost:5001"]
}' "http://{hostname}/nodes/register"
```

### Resolve nodes conflict

```
curl http://{hostname}/nodes/resolve
```

### Mining

```
curl http://{hostname}/mine
```

### Get chain

```
curl http://{hostname}/chain
```
