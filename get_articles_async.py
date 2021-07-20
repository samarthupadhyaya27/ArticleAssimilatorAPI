import json
import asyncio
import aiohttp
import random
from typing import Tuple

# Object to store the articles along with information about them
class article_obj:
    def __init__(self, title: str, word_count: int, url: str):
        self.title = title
        self.word_count = word_count
        self.url = url
    def __str__(self):
        return 'title: ' + self.title + ', words: ' + str(self.word_count) + ', url: ' + self.url

class all_articles:
    def __init__(self):
        self.articles_list = []

        # TODO article choosing and sorting from the pile

    def populate_articles_list(self, themes, websites):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.populate_articles_list_helper(themes, websites))

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
                    theme = theme.strip().replace(' ', '%20').lower()
                    if website == 'nytimes':
                        tasks.append(self.nytimes_search(session, theme))
                    if website == 'medium':
                        tasks.append(self.medium_search(session, theme))
            # Run all the collected tasks asynchronously
            await asyncio.gather(*tasks)

    async def nytimes_search(self, session: aiohttp.ClientSession, theme: str):
        api_key = 'YfU0SYYg6sXIPYAch9b5WHRtN5UfXwAQ'
        api_request_url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json?q=theme&api-key='
        api_request_url = api_request_url.replace("theme", theme)
        api_request_url += api_key
        # Make an request from the New York Times api
        async with session.get(api_request_url) as response:
            # Check if the response was valid
            if response.status != 200:
                # If the response is invalid return
                return
            # Turn the object into a python dictionary
            try:
                response_object_text = await response.text()
                response_object = json.loads(response_object_text)
            except ValueError as e:
                print(e)
                return
            # Create a list with all the array objects returned
            for article in response_object['response']['docs']:
                # Correctly destructure the json object
                try:
                    article_headline = article['headline']['main']
                    word_count = article['word_count']
                    url = article['web_url']
                    if word_count != 0 and article_headline != '' and url != '':
                        article_object = article_obj(article_headline, word_count, url)
                        self.articles_list.append(article_object)
                except KeyError as e:
                    print("KeyError",e)

    async def medium_search(self, session: aiohttp.ClientSession, theme: str):
        api_request_url = 'https://medium.com/tag/theme'
        api_request_url = api_request_url.replace('theme', theme)
        #Make a request to medium to search by themes
        async with session.get(api_request_url) as response:
            if response.status != 200:
              # If the response is invalid return
              return
            #Get a string containing the json from the response text
            response_object_text = await response.text()
            response_json_string = response_object_text.split('APOLLO_STATE__ =')[1].split('</script><middlewarestate>')[0]
            #Turn the object into a python dictionary
            try:
                response_object = json.loads(response_json_string)
            except ValueError as e:
                print("ValueError", e)
                return
            #Create a list with all the array objects returned
            for key in response_object:
                if (key.startswith('Post:')):
                    # Correcty destructure the json object
                    try:
                        article_headline = response_object[key]['title']
                        # Medium sets the average reading speed to be 250 words per minute
                        word_count = round(250 * response_object[key]['readingTime'])
                        url = response_object[key]['mediumUrl']
                        # If all the fields are not empty add the object you want
                        if word_count != 0 and article_headline != '' and url != '':
                            article_object = article_obj(article_headline, word_count, url)
                            self.articles_list.append(article_object)
                    except KeyError as e:
                        print("KeyError", e)

    def provide_articles_by_reading_time(self, reading_time: int, reading_speed: int) -> Tuple[list, int]:
      # List of articles to be returned
      articles_to_present = []
      time = 0
      # Fill the list with articles, ensuring that we get reasonably close to the reading time
      while (time < (reading_time - 5)) and (len(self.articles_list) != 0):
        # Use a random variable as an index into the list
        random_variable = random.randint(0, len(self.articles_list) - 1)
        # Add an article to the list of articles to be presented
        articles_to_present.append(self.articles_list[random_variable])
        # Update the reading time
        time = time + ((self.articles_list[random_variable].word_count) / reading_speed)
        # Remove the used article from the list
        self.articles_list.remove(self.articles_list[random_variable])
        # If the reading time is now too long pop the article that made the reading time too long
        if time > reading_time:
          articles_to_present.pop()
      return (articles_to_present, time)
