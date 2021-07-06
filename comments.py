#requests
import urllib
import json

#selenium web scraping
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

#data collection
import pandas as pd

#google sheets writing
import gspread
from gspread_dataframe import set_with_dataframe

#misc.
from datetime import datetime
from math import ceil
import time

import facebook

class nyt:
	def __init__(self, api_key):
		self.api_key = api_key
		self.comments_list = []

		self.nytimes_write_to_gsheet()
		
	def nytimes_article_total_comments(self, article_url):
		#obtain the total number of parent comments from a given article

		comment_bucket = "http://api.nytimes.com/svc/community/v3/user-content/recent.json?api-key=" + self.api_key + "&offset=0" + "&url=" + article_url
		
		nytimes_request = urllib.request.Request(comment_bucket)
		nytimes_request.add_header('User-Agent', '/Users/rueda/opt/anaconda3/lib/python3.8/urllib/request.py')

		comment_response = urllib.request.urlopen(nytimes_request , timeout=100).read()
		comment_response_dictionary = json.loads(comment_response)

		totalComments = comment_response_dictionary['results']['totalParentCommentsFound']
		totalReplyCommentsFound = comment_response_dictionary['results']['totalReplyCommentsFound']

		num_pages_comments = ceil(totalComments/25)
		return num_pages_comments

	def nytimes_one_page(self, article_url, offset):
		#obtain a single batch of comments from an article (25 comments)

		try:
			comment_bucket = "http://api.nytimes.com/svc/community/v3/user-content/recent.json?api-key=" + self.api_key + "&offset=" + str(offset) + "&url=" + article_url   
		
			nytimes_request = urllib.request.Request(comment_bucket)
			nytimes_request.add_header('User-Agent', '/Users/rueda/opt/anaconda3/lib/python3.8/urllib/request.py')

			comment_response = urllib.request.urlopen(nytimes_request, timeout=100).read()
			comment_response_dictionary = json.loads(comment_response)

			for val in comment_response_dictionary['results']['comments']:
				createDate = int(val['createDate'])
				createDate = datetime.utcfromtimestamp(createDate).strftime('%Y-%m-%d')
				info = [article_url, val['commentBody'], createDate, val['userDisplayName']]
				self.comments_list.append(info)

		except urllib.error.HTTPError as e:
			if(e.code == 429):
				time.sleep(5)
				self.nytimes_one_page(article_url, offset)

	def nytimes_get_comments(self, article_url):
		#get all the comments from an article 

		counter = 0
		num_pages = self.nytimes_article_total_comments(article_url)

		while(counter != num_pages):
			self.nytimes_one_page(article_url, counter)
			counter += 1

	def nytimes_get_articles_from_spreadsheet(self):
		#obtain nytimes articles from spreadsheet

		nytimes_list = []

		df = pd.read_html("https://docs.google.com/spreadsheets/d/1pHTwxtRObCdW6ObcZcn-vwKYO2ii2tdaPhjXAv-P0Sg/edit#gid=0", 
		                  header=1)[0]
		df.drop(columns='1', inplace=True)

		for index, row in df.iterrows():
			if("nytimes.com" in str(row['Link']) and (str(row['Comments (Y/N)']) == "Yes") and (str(row['Fits Definition']) == "Yes")):
				val = row['Link']

				article = val[:val.index(".html") + len(".html")]
				nytimes_list.append(article)

		return nytimes_list

	def nytimes_get_dataframe(self):
		nytimes_list = self.nytimes_get_articles_from_spreadsheet()

		for article in nytimes_list:
			self.nytimes_get_comments(article)

		comments_df = pd.DataFrame(self.comments_list, columns = ['URL', 'Comment Body', 'Date', 'User Display Name'])
		return comments_df

	def nytimes_sort_by_date(self, data):
		dataframe = data.sort_values(by = "Date")
		dataframe.reset_index(inplace=True)
		del dataframe["index"]

		return dataframe

	def nytimes_write_to_gsheet(self):
		#access google sheet
		my_file_path = "/Users/rueda/Desktop/nytscraper-505631f90299.json"

		gc = gspread.service_account(filename = my_file_path)
		sh = gc.open('Comments Scraper')
		worksheet = sh.get_worksheet(0)

		data = self.nytimes_get_dataframe()
		sorted_data = self.nytimes_sort_by_date(data)

		#write all the comments from the dataframe into the sheet
		set_with_dataframe(worksheet, sorted_data)

class fivethirtyeight:
	def __init__(self, api_key):
		#self.soup = BeautifulSoup("https://projects.fivethirtyeight.com/2020-election-forecast/", 'html.parser').contents()
		my_chomedriver_path = '/Users/rueda/Downloads/chromedriver'
		self.driver = webdriver.Chrome(my_chomedriver_path)
		self.comments_list = []
		self.api_key = api_key

		self.fivethirtyeight_write_to_gsheet()

		self.driver.close()
		
	def fivethirtyeight_get_articles_from_spreadsheet(self):

		fivethirtyeight_list = []

		df = pd.read_html("https://docs.google.com/spreadsheets/d/1pHTwxtRObCdW6ObcZcn-vwKYO2ii2tdaPhjXAv-P0Sg/edit#gid=0", 
		                  header=1)[0]
		df.drop(columns='1', inplace=True)

		for index, row in df.iterrows():
			if("projects.fivethirtyeight.com" in str(row['Link']) and (str(row['Comments (Y/N)']) == "Yes") and (str(row['Fits Definition']) == "Yes")):
				article = row['Link']
				fivethirtyeight_list.append(article)

		return fivethirtyeight_list

	def fivethirtyeight_plugin_url(self, article_url):
		self.driver.get(article_url)
		self.driver.find_element_by_class_name("fte-expandable-icon").click()
		time.sleep(5)

		fivethirtyeight_plugin_url = self.driver.find_element_by_xpath('//*[@id="fb-comments"]/span/iframe').get_attribute("src")
		return fivethirtyeight_plugin_url

	def fivethirtyeight_facebook_request(self, article_url):
		fivethirtyeight_plugin_url = self.fivethirtyeight_plugin_url(article_url)
		comment_bucket = "https://graph.facebook.com/v2.6/?fields=og_object{comments}&id=" + article_url + "&access_token=" + self.api_key

		make_facebook_request = urllib.request.Request(comment_bucket)

		facebook_response = urllib.request.urlopen(make_facebook_request, timeout=100).read()
		facebook_response_dictionary = json.loads(facebook_response)

		return facebook_response_dictionary

	def fivethirtyeight_one_page(self, article_url):
		facebook_response_dictionary = self.fivethirtyeight_facebook_request(article_url)

		for article in facebook_response_dictionary['og_object']['comments']['data']:
			created_time = str(article['created_time'])[:10]

			info = [article_url, article['message'], created_time]
			self.comments_list.append(info)

	def fivethirtyeight_get_dataframe(self):
		fivethirtyeight_list = self.fivethirtyeight_get_articles_from_spreadsheet()

		for article in fivethirtyeight_list:
			self.fivethirtyeight_one_page(article)

		comments_df = pd.DataFrame(self.comments_list, columns = ['URL', 'Comment Body', 'Date'])
		return comments_df

	def fivethirtyeight_sort_by_date(self, data):
		dataframe = data.sort_values(by = "Date")
		dataframe.reset_index(inplace=True)
		del dataframe["index"]

		return dataframe

	def fivethirtyeight_write_to_gsheet(self):
		#access google sheet
		my_file_path = "/Users/rueda/Desktop/nytscraper-505631f90299.json"

		gc = gspread.service_account(filename = my_file_path)
		sh = gc.open('Comments Scraper')
		worksheet = sh.get_worksheet(1)

		data = self.fivethirtyeight_get_dataframe()
		sorted_data = self.fivethirtyeight_sort_by_date(data)

		#write all the comments from the dataframe into the sheet
		set_with_dataframe(worksheet, sorted_data)

# my_nytimes_key = "8inUMyZeiS3REM7tN4KbE20dktQG1eEG"
# a = nyt(my_nytimes_key)

my_fivethirtyeight_key = "EAAoFCPRflZBABACnbImrBiOtvzO0zORRHOWxfVAgYehbKVDr3erMU17KRJ5BihOJrS8x2qwH58QyuirpweO923T6RNgt3Vp7m7iW6SZAXlZCo04tx7gY5oGiLUZBiJ84WwdmuoWxa7ZBYPrj9PjkfwJOTEUk3ZC3OUhuQebgoxnbqZAdV32Jh1TxXt0NZBFQR9JPugmZCWRsXxHNqwk7PAJHlEloRJUdUyO7nLBoRd0lgaMCX5YF8KRInnMGUkWaYEpUZD"
b = fivethirtyeight(my_fivethirtyeight_key)
