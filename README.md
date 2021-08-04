# Journalism Scrapers
[![Email][email-shield]][email-url]
[![LinkedIn][linkedin-shield]][linkedin-url]
[![License][license-shield]][license-url]
[![License][python-shield]][python-url]


A collection of scripts that scrape and format comments from several major news publications.

## Getting Started

### Dependencies
Install the following dependencies in your terminal.

* [selenium]()
* [pandas]()
* [gspread]()
* [gspread_dataframe]()
* [datetime]()

Use the command 
```
pip install
```


### New York Times Scraper Requirements
In order to use the scraper to obtain any user comments, you must have a New York Times [Developer API key.](https://developer.nytimes.com/apis)

### FiveThirtyEight Scraper Requirements
In order to use the scraper to obtain any user comments, you must have a Facebook Developers [User Accesss Token.](https://developers.facebook.com/)

In addition, you must have [Selenium](https://www.selenium.dev/) and [ChromeDriver](https://chromedriver.chromium.org/) installed.

### Washington Post Scraper Requirements
In order to use the scraper to obtain any user comments, you must have [Selenium](https://www.selenium.dev/) and [ChromeDriver](https://chromedriver.chromium.org/) installed.

### Additional Requirements
In order to use the scrapers' ```write_to_gsheet()``` methods, you must have service account and OAuth2 credentials from the [Google API Console.](https://console.cloud.google.com/apis/dashboard)

## Limitations
The New York Times scraper obtains a comment's Article URL, Parent ID, Comment ID, User Display Name, Comment Body, Upload Date, Number of Likes, Number of Replies, and Editor's Selection.

The Washington Post scraper obtains a comment's Article URL, User Display Name, Comment Body, Upload Date, and Number of Likes.

The FiveThirtyEight scraper obtains a comment's Article URL, Comment Body, and Upload Date.

## Code Walkthrough
Begin by initializing a new instance of your desired scraper.
```python
WaPo_Scraper = washingtonpost(my_chromedriver_path)
NYT_Scraper = nyt(my_api_key)
FiveThirtyEight_Scraper = fivethirtyeight(my_token, my_chomedriver_path)
```

You can retrieve a list of comments from a single article using the article URL with the ```get_article_comments()``` method.
```python

my_article = "https://www.washingtonpost.com/politics/2021/04/13/risk-reward-calculus-johnson-johnson-vaccine-visualized/"
WaPo_Scraper.get_article_comments(my_article)
```

You can retrieve a list of comments from a list of articles with the ```get_comments_from_multiple_articles()``` method.
```python

my_article_list = ["https://www.nytimes.com/2015/04/12/opinion/sunday/david-brooks-the-moral-bucket-list.html", "https://www.nytimes.com/2019/06/21/science/giant-squid-cephalopod-video.html", "https://www.nytimes.com/2021/08/01/insider/the-olympics-that-feel-like-only-competitions.html"]

NYT_Scraper.get_comments_from_multiple_articles(my_article_list)

```

You can retrieve a list of articles from a Google Spreadsheet with the ```get_articles_from_spreadsheet()``` method.
```python

FiveThirtyEight_Scraper.get_articles_from_spreadsheet(spreadsheet_url, sheet_number)
```

You can convert a list of comments into a Pandas dataframe with the ```get_dataframe()``` method.
```python

WaPo_Scraper.get_dataframe(comments_list)
```

You can write a dataframe of comments into a Google Spreadsheet with the ```write_to_gsheet()``` method.
```python

NYT_Scraper.write_to_gsheet(dataframe, gsheet_path, gsheet_name, sheet_number)
```


[email-shield]: https://img.shields.io/badge/EMAIL-rueda.kv%40gmail.com%20-brightgreen?style=for-the-badge&colorB=critical
[email-url]: mailto:rueda.kv@gmail.com

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=critical
[linkedin-url]: https://linkedin.com/in/RuedaKV

[license-shield]: https://img.shields.io/github/license/RuedaKV/comments?style=for-the-badge&colorB=critical
[license-url]: https://github.com/RuedaKV/comments/blob/master/LICENSE.txt

[python-shield]: https://img.shields.io/badge/-python-black.svg?style=for-the-badge&logo=python&colorB=critical
[python-url]: https://www.python.org/downloads/release/python-388/

