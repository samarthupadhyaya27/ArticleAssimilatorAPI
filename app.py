from flask import Flask, request
from get_articles_async import all_articles
import os
import logging
import sys

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)


@app.route('/', methods=['GET'])
def getArticles():
    res = request.args.getlist('foo[]')
    print("request.args.get('q'):", res)
    all_articles_object = all_articles()
    return "<h1>Working router</h1>"



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
