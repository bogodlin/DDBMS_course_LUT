import json

def retrieve_host(type):
    with open('config.json') as f:
        data = json.load(f)
        for platform in data['platforms']:
            if platform['type'] == type:
                host = platform['host']
    return host

def retrieve_port(type):
    with open('config.json') as f:
        data = json.load(f)
        for platform in data['platforms']:
            if platform['type'] == type:
                port = platform['port']
    return port