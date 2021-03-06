import json
import asyncio
import aiohttp
import Constants
import random
from typing import Tuple


# Object to store the articles along with information about them
class ArticleObject:
    def __init__(self, title: str, word_count: int, url: str):
        self.title = title
        self.word_count = word_count
        self.url = url

    def __str__(self):
        return (
            "title: "
            + self.title
            + ", words: "
            + str(self.word_count)
            + ", url: "
            + self.url
        )


class AllArticles:
    def __init__(self):
        self.articles_list = []

    def populate_articles_list(self, themes: list, websites: list):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            self.populate_articles_list_helper(themes, websites))
        loop.close()

    async def populate_articles_list_helper(self, themes: list, websites: list):
        # Collect all the tasks to be executed async
        tasks = []
        # Pass down an aiohttp client session to each process
        async with aiohttp.ClientSession() as session:
            # Iterate through every website
            for website in websites:
                # And through all the themes in each website
                for theme in themes:
                    # Format the theme string correctly
                    theme = theme.strip().replace(" ", "%20").lower()
                    if website == "nytimes":
                        tasks.append(self.nytimes_search(session, theme))
                    if website == "medium":
                        tasks.append(self.medium_search(session, theme))
            # Run all the collected tasks asynchronously
            await asyncio.gather(*tasks)

    async def nytimes_search(self, session: aiohttp.ClientSession, theme: str):
        api_request_url = (
            "https://api.nytimes.com/svc/search/v2/articlesearch.json?q=theme&api-key="
        )
        api_request_url = api_request_url.replace("theme", theme)
        api_request_url += Constants.NY_TIMES_API_KEY
        # Make an request from the New York Times api
        async with session.get(api_request_url) as response:
            # Check if the response was valid
            if response.status != 200:
                # If the response is invalid return
                print("Invalid Response", response.status)
                return
            # Turn the object into a python dictionary
            try:
                response_object_text = await response.text()
                response_object = json.loads(response_object_text)
            except ValueError as e:
                print("ValueError", e)
                return
            # Create a list with all the array objects returned
            for article in response_object["response"]["docs"]:
                # Correctly destructure the json object
                try:
                    article_headline = article["headline"]["main"]
                    word_count = article["word_count"]
                    url = article["web_url"]
                    if word_count != 0 and article_headline != "" and url != "":
                        article_object = ArticleObject(
                            article_headline, word_count, url
                        )
                        self.articles_list.append(article_object)
                except KeyError as e:
                    print("KeyError", e)

    async def medium_search(self, session: aiohttp.ClientSession, theme: str):
        api_request_url = "https://medium.com/tag/theme"
        api_request_url = api_request_url.replace("theme", theme)
        # Make a request to medium to search by themes
        async with session.get(api_request_url) as response:
            if response.status != 200:
                # If the response is invalid return
                return
            # Get a string containing the json from the response text
            response_object_text = await response.text()
            response_json_string = response_object_text.split("APOLLO_STATE__ =")[
                1
            ].split("</script><script>window.__MIDDLEWARE_STATE__=")[0]
            # Turn the object into a python dictionary
            try:
                response_object = json.loads(response_json_string)
            except ValueError as e:
                print("ValueError", e)
                return
            # Create a list with all the array objects returned
            for key in response_object:
                if key.startswith("Post:"):
                    # Correcty destructure the json object
                    try:
                        article_headline = response_object[key]["title"]
                        # Medium sets the average reading speed
                        # to be 250 words per minute
                        word_count = round(
                            250 * response_object[key]["readingTime"])
                        url = response_object[key]["mediumUrl"]
                        # If all the fields are not empty add
                        # the object you want
                        if word_count != 0 and article_headline != "" and url != "":
                            article_object = ArticleObject(
                                article_headline, word_count, url
                            )
                            self.articles_list.append(article_object)
                    except KeyError as e:
                        print("KeyError", e)

    async def guardian_search(self, session: aiohttp.ClientSession, theme: str):
        # TODO
        pass

    def provide_articles_by_reading_time(
        self, reading_time: int, reading_speed: int
    ) -> Tuple[list, int]:
        # List of articles to be returned
        articles_to_present = []
        time = 0
        # Fill the list with articles, ensuring that we get
        # reasonably close to the reading time
        while (time < (reading_time * 0.80)) and (len(self.articles_list) != 0):
            # Use a random variable as an index into the list
            random_variable = random.randint(0, len(self.articles_list) - 1)
            # Get a random article
            random_article = self.articles_list[random_variable]
            # Add an article to the list of articles to be presented
            articles_to_present.append(
                {
                    "title": random_article.title,
                    "word_count": random_article.word_count,
                    "url": random_article.url,
                }
            )
            # Increment the total reading time
            time += random_article.word_count / reading_speed
            # Remove the used article from the list
            self.articles_list.remove(random_article)
            # If the reading time is now too long pop the
            # article that made the reading time too long
            if time > reading_time:
                articles_to_present.pop()
        return (articles_to_present, time)
