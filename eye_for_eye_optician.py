from eye_for_eye_optician import app
import json

if __name__ == '__main__':

    with open('config.json') as f:
        data = json.load(f)
        for platform in data['platforms']:
            if platform['type'] == "optician":
                port = platform['port']

    app.run(debug=True, threaded=True, port=port)
