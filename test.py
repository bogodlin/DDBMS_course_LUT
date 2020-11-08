import json

with open('config.json') as f:
    data = json.load(f)
    for app in data['applications']:
        if app['type'] == "optician":
            port = app['port']

