# Comments Scraper

A collection of scripts that scrape and format comments from several major news publications.

### New York Times Scraper Requirements
In order to use the scraper to obtain any user comments, you must have a New York Times Developer API key. You may register for an API key [here.](https://developer.nytimes.com/apis)

### FiveThirtyEight Scraper Requirements
In order to use the scraper to obtain any user comments, you must have a Facebook Developers User Accesss Token. You can obtain one [here.](developers.facebook.com)

In addition, you must have [Selenium](https://www.selenium.dev/) and [ChromeDriver](https://chromedriver.chromium.org/) installed.

### Washington Post Scraper Requirements
In order to use the scraper to obtain any user comments, you must have [Selenium](https://www.selenium.dev/) and [ChromeDriver](https://chromedriver.chromium.org/) installed.

### Features

#### Code Example
Begin by initializing a new instance of your desired scraper.
```
WaPo_Scraper = washingtonpost(my_chromedriver_path)
NYT_Scraper = nyt(my_api_key)
FiveThirtyEight_Scraper = fivethirtyeight(my_token, my_chomedriver_path)
```

You can retrieve a list of comments from a single article.
```
WaPo_Scraper.get_article_comments()
NYT_Scraper.get_article_comments("https://www.nytimes.com/2015/04/12/opinion/sunday/david-brooks-the-moral-bucket-list.html)
FiveThirtyEight_Scraper.get_article_comments("https://projects.fivethirtyeight.com/2020-election-forecast/")
```

You can retrieve a list from a single article 
