import requests
import json
import time

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
        self.all_collected_articles = []

        # TODO article choosing and sorting from the pile

    def populate_all_collected_articles(self, themes: list, websites: list):
        # Iterate through every website
        for website in websites:
        # And through all the themes in each website
            for theme in themes:
                theme = theme.strip().replace(' ', '%20').lower()
                if website == 'nytimes':
                    articles = self.nytimes_search(theme)
                    self.all_collected_articles.append(articles)
                if website == 'medium':
                    articles = self.medium_search(theme)
                    self.all_collected_articles.append(articles)
                if website == 'bloomberg':
                    articles = self.bloomberg_search(theme)
                    self.all_collected_articles.append(articles)

    def nytimes_search(self, theme: str) -> list:
        api_key = 'YfU0SYYg6sXIPYAch9b5WHRtN5UfXwAQ'
        api_request_url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json?q=theme&api-key='
        api_request_url.replace('theme', theme)
        # Make an request from the New York Times api
        response = requests.get(api_request_url + api_key)
        # Check if the response was valid
        if response.status_code != 200:
            # If the response is invalid return
            return []
        # Turn the object into a python dictionary
        try:
            response_object = json.loads(response.text)
        except ValueError as e:
            print(e)
            return []
        # Create a list with all the array objects returned
        articles = []
        for article in response_object['response']['docs']:
            # Correctly destructure the json object
            try:
                article_headline = article['headline']['main']
                word_count = article['word_count']
                url = article['web_url']
                if word_count != 0 and article_headline != '' and url != '':
                    article_object = article_obj(article_headline, word_count, url)
                    articles.append(article_object)
            except KeyError as e:
                print("KeyError",e)
        # Return the list of collected articles
        print(len(articles))
        return articles

    def medium_search(self, theme: str) -> list:
        api_request_url = 'https://medium.com/tag/theme'
        api_request_url = api_request_url.replace('theme', theme)
        #Make a request to medium to search by themes
        response = requests.get(api_request_url)
        if response.status_code != 200:
          # If the response is invalid return
          return []
        #Get a string containing the json from the response text
        response_json_string = response.text.split('APOLLO_STATE__ =')[1].split('</script><middlewarestate>')[0]
        #Turn the object into a python dictionary
        try:
            response_object = json.loads(response_json_string)
        except ValueError as e:
            print("ValueError", e)
            return []
        #Create a list with all the array objects returned
        articles = []
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
                        articles.append(article_object)
                except KeyError as e:
                    print("KeyError", e)
                    print(e)
        print(len(articles))
        return articles
    def bloomberg_search(self, theme: str) -> list:
        # TODO
        return []


start = time.time()
all_articles_object = all_articles()
all_articles_object.populate_all_collected_articles(["science", "politics", "economics", "sports", "literature", "technology"], ["medium", "nytimes"])
end = time.time()

# for collection in all_articles_object.all_collected_articles:
#   for article in collection:
#     print(article)
print(end - start)
