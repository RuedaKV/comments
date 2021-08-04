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
from gspread_dataframe import set_with_dataframe, get_as_dataframe

#misc.
from datetime import datetime
from math import ceil
import time

import facebook

import pickle

class fivethirtyeight:
	def __init__(self, api_key, chomedriver_path):
		"""Initialize empty comments list and webdriver. Execute code to obtain and aggregate comments. Write comments into a Google Spreadsheet"""

		self.driver = webdriver.Chrome(chomedriver_path)
		self.api_key = api_key
		
	def get_articles_from_spreadsheet(self, spreadsheet_url, sheet_number):
		"""Returns a list of Fivethirtyeight articles from the spreadsheet"""

		fivethirtyeight_list = []

		df = pd.read_html(spreadsheet_url, 
		                  header=1)[sheet_number]
		df.drop(columns='1', inplace=True)

		for index, row in df.iterrows():
			if("projects.fivethirtyeight.com" in str(row['Link']) and (str(row['Comments (Y/N)']) == "Yes") and (str(row['Fits Definition']) == "Yes")):
				article = row['Link']
				fivethirtyeight_list.append(article)

		return fivethirtyeight_list

	def get_plugin_url(self, article_url):
		"""Returns the Facebook plug-in url for an article's comments section"""

		self.driver.get(article_url)
		self.driver.find_element_by_class_name("fte-expandable-icon").click()
		time.sleep(5)

		fivethirtyeight_plugin_url = self.driver.find_element_by_xpath('//*[@id="fb-comments"]/span/iframe').get_attribute("src")

		return fivethirtyeight_plugin_url

	def make_facebook_request(self, article_url):
		"""Returns a dictionary from a Facebook request"""

		fivethirtyeight_plugin_url = self.get_plugin_url(article_url)
		comment_bucket = "https://graph.facebook.com/v2.6/?fields=og_object{comments}&id=" + article_url + "&access_token=" + self.api_key

		make_facebook_request = urllib.request.Request(comment_bucket)

		facebook_response = urllib.request.urlopen(make_facebook_request, timeout=100).read()
		facebook_response_dictionary = json.loads(facebook_response)

		return facebook_response_dictionary

	def one_page(self, article_url):
		"""Returns a list of comments from a single Fivethirtyeight article"""

		comments_list = []

		facebook_response_dictionary = self.make_facebook_request(article_url)

		for article in facebook_response_dictionary['og_object']['comments']['data']:
			created_time = str(article['created_time'])[:10]

			info = [article_url, article['message'], created_time]
			comments_list.append(info)

		return comments_list

	def get_comments_from_multiple_articles(self, articles_list):
		"""Returns a list containing all the comments from the articles list"""

		comments_list = []

		for article in articles_list:
			comments_list += self.one_page(article)

		return comments_list

	def get_dataframe(self, comments_list):
		"""Converts a list of comments into a Pandas dataframe"""

		comments_df = pd.DataFrame(comments_list, columns = ['URL', 'Comment Body', 'Date'])
		return comments_df

	def sort_by_date(self, data):
		"""Return a sorted dataframe"""

		dataframe = data.sort_values(by = "Date")
		dataframe.reset_index(inplace=True)
		del dataframe["index"]

		return dataframe

	def write_to_gsheet(self, dataframe, gsheet_path, gsheet_name, sheet_number):
		"""Write the dataframe in a Google Spreadsheet"""

		gc = gspread.service_account(filename = gsheet_path)
		sh = gc.open(gsheet_name)
		worksheet = sh.get_worksheet(sheet_number)

		set_with_dataframe(worksheet, dataframe)
