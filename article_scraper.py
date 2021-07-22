from urllib.request import urlopen, HTTPError, Request
from bs4 import BeautifulSoup
import Levenshtein
import random

# Supported services -> medium, ...

# Will be done using API calls for websites


class article_obj:
    def __init__(self, title, word_count, url):
        self.title = title
        self.word_count = word_count
        self.url = url

    def __str__(self):
        return (
            "title: "
            + self.title
            + ", reading: "
            + self.word_count
            + ", url: "
            + self.url
        )


class all_articles:
    def __init__(self, themes, websites):
        self.articles_list = []
        # list full of article objects
        for website in websites:
            # Check through each of the websites
            for theme in themes:
                if website == "medium":
                    self.medium_search_by_themes(theme)
                # search medium for articles with the given theme
                if website == "nytimes":
                    print("running")
                    self.nytimes_search_by_themes(theme)

    def get_beautifulsoup_webpage(self, url):
        # method to get a beautiful soup object for a page
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            html = urlopen(req)
        except HTTPError as e:

            # print("HTTPError")
            return None
        try:
            webpage = BeautifulSoup(html.read(), "lxml")

        # print(webpage)
        except AttributeError as e:

            # print("AttributeError")
            return None
        return webpage

    def nytimes_search_by_themes(self, theme):
        theme = theme.strip().replace(" ", "%20")
        url = (
            "https://www.nytimes.com/search?dropmab=false&query="
            + theme
            + "&sort=best&types=article"
        )
        webpage = self.get_beautifulsoup_webpage(url)
        articles = webpage.find_all("h4", class_="css-2fgx4k")
        if not articles:
            return
        if len(articles) > 5:
            article_body = articles[0:5]
        for article in article_body:
            url_2 = "http://www.nytimes.com/" + \
                article.find_parent("a")["href"]
            url_2 = url_2.split("?")[0]
            webpage_2 = self.get_beautifulsoup_webpage(url_2)
            article_body = webpage_2.find(
                "section", class_="meteredContent css-1r7ky0e"
            )
            text_string = ""
            for text_section in article_body.find_all("p"):
                text_string = text_string + " " + text_section.text
            word_count = text_string.count(" ")
            title = article.text
            article_object = article_obj(title, word_count, url_2)
            self.articles_list.append(article_object)

    def medium_search_by_themes(self, theme):
        theme = theme.strip().replace(" ", "%20")
        url = "https://medium.com/search/tags?q=" + theme
        webpage = self.get_beautifulsoup_webpage(url)
        tags = webpage.find_all("a", class_="link u-baseColor--link")

        # print(tags)
        if not tags:
            # checking if the tags beautiful soup object is not empty
            return
        tags_to_url = {}
        levenshtein_distance_dict = {}
        for a in tags:
            tags_to_url[a.text.lower()] = a["href"]
            # setting each of the tags to a url
            levenshtein_distance_dict[a.text.lower()] = Levenshtein.distance(
                theme, a.text.lower()
            )
        # making a dictionary mapping the theme names to their Levenshtein distance
        min_distance_key = min(
            levenshtein_distance_dict, key=levenshtein_distance_dict.get
        )
        # finding the name of the theme closest matching the users input
        url_2 = tags_to_url[min_distance_key]
        # find the url of the tag that matches the given theme most closely
        webpage_2 = self.get_beautifulsoup_webpage(url_2)
        # get a beautiful soup rendering of the page with articles relating to that theme
        articles = webpage_2.find_all(
            "div",
            class_="cardChromeless u-marginTop20 u-paddingTop10 u-paddingBottom15 u-paddingLeft20 u-paddingRight20",
        )
        while (len(articles) <= 0) & (len(levenshtein_distance_dict) >= 0):
            del levenshtein_distance_dict[min_distance_key]
            min_distance_key = min(
                levenshtein_distance_dict, key=levenshtein_distance_dict.get
            )
            # finding the name of the theme next closest matching the users input
            url_2 = tags_to_url[min_distance_key]
            # find the url of the tag that matches the given theme most closely
            webpage_2 = self.get_beautifulsoup_webpage(url_2)
            articles = webpage_2.find_all(
                "div",
                class_="cardChromeless u-marginTop20 u-paddingTop10 u-paddingBottom15 u-paddingLeft20 u-paddingRight20",
            )
        if len(articles) > 7:
            # If there are more than 5 articles for a tag, limit to any searching for 5 articles
            articles = articles[0:7]
        if len(articles) > 0:
            for article in articles:
                try:
                    title = article.h3.text
                    reading_time = article.find("span", class_="readingTime").get(
                        "title"
                    )[0]
                    words_in_article = int(reading_time) * 250
                    url = article.find(
                        "a", class_="link link--darken").get("href")
                    article_object = article_obj(title, words_in_article, url)
                    # create an object that contains the details about each article
                    self.articles_list.append(article_object)
                except AttributeError as e:
                    continue

    def provide_articles_by_reading_time(self, reading_time, reading_speed):
        articles_to_present = []
        time = 0
        while (time < (reading_time - 5)) and (len(self.articles_list) != 0):
            # Set the criteria between which articles can be served
            random_variable = random.randint(0, len(self.articles_list) - 1)
            # get a random variable to randomly search through the articles collected
            articles_to_present.append(self.articles_list[random_variable])
            # Add the article tot he list of articles to present
            time = time + (
                (int(self.articles_list[random_variable].word_count))
                / int(reading_speed)
            )
            self.articles_list.remove(self.articles_list[random_variable])
            # Remove the article from the list of all articles collected
            if time > reading_time:
                # Ensure the time is not greater than the reading time
                articles_to_present.pop()
        return (articles_to_present, time)


# themes = ['technology', 'math']
# websites = ['Medium']
#
# articles = all_articles(themes, websites)
# presented_articles = articles.provide_articles_by_reading_time(40)
# for i in presented_articles:
#     print(i.title)
#     print(i.reading_duration)
