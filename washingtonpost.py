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

class washingtonpost:
	def __init__(self, chromedriver_path):
		self.chomedriver_path = chromedriver_path
		self.driver = webdriver.Chrome(self.chomedriver_path)

	def get_articles_from_spreadsheet(self, spreadsheet_url, sheet_number):
		"""Return a list of the Washington Post articles from a spreadsheet"""

		washingtonpost_list = []

		df = pd.read_html(spreadsheet_url, 
	                  	header=1)[sheet_number]
		df.drop(columns='1', inplace=True)

		for index, row in df.iterrows():
			if("washingtonpost.com" in str(row['Link']) and (str(row['Comments (Y/N)']) == "Yes") and (str(row['Fits Definition']) == "Yes")):
				article = row['Link']
				washingtonpost_list.append(article)

		return washingtonpost_list

	def get_article_comments(self, article_url):
		"""Returns a list of all article comments"""

		comments_list = []

		plugin = "https://talk.washingtonpost.com/embed/stream?storyURL="
		plugin += article_url

		self.driver.get(plugin)
		time.sleep(5)

		try:
			self.driver.find_element_by_xpath('//*[@id="tab-ALL_COMMENTS"]/button').click()
		except:
			pass

		time.sleep(5)

		while True:
			try:
				self.driver.find_element_by_css_selector("#comments-loadMore").click()
				time.sleep(5)
			except:
				break

		comment_text_xpath = '(//*[contains(@class, "coral-comment-content")])'
		comment_text_element = list(self.driver.find_elements_by_xpath(comment_text_xpath))

		comment_text_list = []
		for comment in comment_text_element:
			comment_text_list.append(comment.text)

		username_xpath = '(//*[contains(@class, "coral-username")])'
		username_element = list(self.driver.find_elements_by_xpath(username_xpath))

		username_list = []
		for username in username_element:
			username_list.append(username.text)

		comment_timestamp_xpath = '(//*[contains(@class, "coral-timestamp")])'
		comment_timestamp = self.driver.find_elements_by_xpath(comment_timestamp_xpath)

		datetime_list = []

		for timestamp in comment_timestamp:
			comment_datetime = timestamp.get_attribute("datetime")[:10]
			datetime_list.append(comment_datetime)

		likes_xpath = '(//*[contains(@class, "coral-comment-reactButton")])'
		comment_likes = self.driver.find_elements_by_xpath(likes_xpath)

		likes_list = []

		for val in comment_likes:

			if(len(val.text) == 8):
				likes = 0
			else:
				likes = int(val.text[9:])

			likes_list.append(likes)

		num_comments = len(comment_text_list)


		zipped_items = zip(username_list, comment_text_list, datetime_list, likes_list)
		zipped_list = list(zipped_items)


		url_list = [article_url]

		for comment in zipped_list:
			info = url_list + list(comment)
			comments_list.append(info)

		return comments_list

	def get_comments_from_multiple_articles(self, articles_list):
		"""Returns all the comments from the list of articles"""

		comments_list = []

		for article in articles_list:
			try:
				article_comments = self.get_article_comments(article)
				comments_list += article_comments
			except:
				continue

		return comments_list

	def get_dataframe(self, comments_list):
		"""Converts a list of comments into a Pandas dataframe"""

		comments_df = pd.DataFrame(comments_list, columns = ["Link", "Display Name", "Comment Body", "Date", "Likes"])
		return comments_df

	def write_to_gsheet(self, dataframe, gsheet_path, gsheet_name, sheet_number):
		"""Write the dataframe in a Google Spreadsheet"""

		gc = gspread.service_account(filename = gsheet_path)
		sh = gc.open(gsheet_name)
		worksheet = sh.get_worksheet(sheet_number)

		set_with_dataframe(worksheet, dataframe)
