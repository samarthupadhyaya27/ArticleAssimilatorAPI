from flask import Flask, request
from get_articles_async import all_articles
import os
import logging
import sys
import json

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)


@app.route("/", methods=["GET"])
def getArticles():
    # Get relevant parameters from the request arguments
    reading_time = request.args.get("reading_time", type=int, default=0)
    reading_speed = request.args.get("reading_speed", type=int, default=250)
    websites = request.args.getlist("websites[]")
    themes = request.args.getlist("themes[]")
    print(websites, themes)
    # Instantiate an all articles object
    all_articles_object = all_articles()
    # Populate the all articles object with the data generated with the input parameters
    all_articles_object.populate_articles_list(themes, websites)
    # Get articles that fit the desired reading time
    (
        returned_articles,
        returned_reading_time,
    ) = all_articles_object.provide_articles_by_reading_time(
        reading_time, reading_speed
    )
    print("returned_reading_time", returned_reading_time)
    for article in returned_articles:
        print(article)
    returned_articles_json = json.dumps(
        {"articles": returned_articles, "reading_time": returned_reading_time}
    )
    return returned_articles_json


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
