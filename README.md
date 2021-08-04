# Comments Scraper

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
In order to use the scrapers' ```python write_to_gsheet()``` methods, you must have service account and OAuth2 credentials from the [Google API Console.](https://console.cloud.google.com/apis/dashboard)

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

You can retrieve a list of comments from a single article using the article URL with the ```w``` method.
```python
WaPo_Scraper.get_article_comments("https://www.washingtonpost.com/politics/2021/04/13/risk-reward-calculus-johnson-johnson-vaccine-visualized/")
NYT_Scraper.get_article_comments("https://www.nytimes.com/2015/04/12/opinion/sunday/david-brooks-the-moral-bucket-list.html")
FiveThirtyEight_Scraper.get_article_comments("https://projects.fivethirtyeight.com/2020-election-forecast/")
```

You can retrieve a list of comments from a list of articles.
```python
WaPo_Scraper.get_comments_from_multiple_articles(list_of_article_urls)
NYT_Scraper.get_comments_from_multiple_articles(list_of_article_urls)
FiveThirtyEight_Scraper.get_comments_from_multiple_articles(list_of_article_urls)
```

You can retrieve a list of articles from a Google Spreadsheet.
```python
WaPo_Scraper.get_articles_from_spreadsheet(spreadsheet_url, sheet_number)
NYT_Scraper.get_articles_from_spreadsheet(spreadsheet_url, sheet_number)
FiveThirtyEight_Scraper.get_articles_from_spreadsheet(spreadsheet_url, sheet_number)
```

You can convert a list of comments into a Pandas dataframe.
```python
WaPo_Scraper.get_dataframe(comments_list)
NYT_Scraper.get_dataframe(comments_list)
FiveThirtyEight_Scraper.get_dataframe(comments_list)
```

You can write a dataframe of comments into a Google Spreadsheet.
```python
WaPo_Scraper.write_to_gsheet(dataframe, gsheet_path, gsheet_name, sheet_number)
NYT_Scraper.write_to_gsheet(dataframe, gsheet_path, gsheet_name, sheet_number)
FiveThirtyEight_Scraper.write_to_gsheet(dataframe, gsheet_path, gsheet_name, sheet_number)
```
