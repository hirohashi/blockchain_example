import argparse
import urllib.request
import json

parser = argparse.ArgumentParser(description="blockchain request")
parser.add_argument('request', type=str, default='/chain', help='kind of api request')
parser.add_argument('--url', type=str, default='http://localhost:5000')
args = parser.parse_args()

if args.request == '/chain':
    req = urllib.request.Request('%s%s' % (args.url, args.request))
    with urllib.request.urlopen(req) as res:
        body = res.read()
        print(body)
elif args.request == '/mine':
    req = urllib.request.Request('%s%s' % (args.url, args.request))
    with urllib.request.urlopen(req) as res:
        body = res.read()
        print(body)
elif args.request == '/transactions/new':
    sender = input('please input sender uuid: ')
    recipient = input('please input recipient: ')
    amount = input('please input amount: ')
    data = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            }
    headers = {
            'Content-Type': 'application/json',
            }
    req = urllib.request.Request('%s%s' % (args.url, args.request), json.dumps(data).encode(), headers)
    with urllib.request.urlopen(req) as res:
        body = res.read()
        print(body)
elif args.request == '/nodes/register':
    nodes = []
    node = input('please input node: ')
    nodes.append(node)
    data = {
            'nodes': nodes
            }
    headers = {
            'Content-Type': 'application/json',
            }
    req = urllib.request.Request('%s%s' % (args.url, args.request), json.dumps(data).encode(), headers)
    with urllib.request.urlopen(req) as res:
        body = res.read()
        print(body)
elif args.request == '/nodes/resolve':
    req = urllib.request.Request('%s%s' % (args.url, args.request))
    with urllib.request.urlopen(req) as res:
        body = res.read()
        print(body)
else:
    print('request is invalid.')
