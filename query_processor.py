from query_processor import app

if __name__ == '__main__':
        app.run(debug=True, threaded=True, port=app.config['PORT'])
