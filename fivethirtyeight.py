#requests
import urllib
import json

#selenium web scraping
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

#data collection
import pandas as pd

#google sheets writing
import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe

#timing
from datetime import datetime
from math import ceil
import time

options = Options()
options.headless = True



class fivethirtyeight:
	def __init__(self):
		"""Initialize empty comments list and webdriver."""

		self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

		
	def get_articles_from_spreadsheet(self, spreadsheet_url, sheet_number):
		"""Returns a list of Fivethirtyeight articles from the spreadsheet"""

		fivethirtyeight_list = []

		df = pd.read_html(spreadsheet_url, 
		                  header=1)[0]
		df.drop(columns='1', inplace=True)

		for index, row in df.iterrows():
			if("projects.fivethirtyeight.com" in str(row['Link']) and (str(row['Comments (Y/N)']) == "Yes") and (str(row['Fits Definition']) == "Yes")):
				article = row['Link']
				fivethirtyeight_list.append(article)

		return fivethirtyeight_list

	def get_plugin_url(self, article_url):
		"""Returns the Facebook plug-in url for an article's comments section"""

		self.driver.get(article_url)
		self.driver.find_element(by=By.CLASS_NAME, value = "fte-expandable-icon").click()
		time.sleep(5)

		fivethirtyeight_plugin_url = self.driver.find_element(by=By.XPATH, value = '//*[@id="entry-comments"]/div/div/span/iframe').get_attribute("src")

		return fivethirtyeight_plugin_url


	def get_article_comments(self, article_url):
		"""Returns a list of comments from a single Fivethirtyeight article"""

		time.sleep(5)

		comments_list = []

		plugin = self.get_plugin_url(article_url)


		self.driver.get(plugin)

		time.sleep(5)

		while True:
			try:
				self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				self.driver.find_element(by=By.CLASS_NAME, value = "_1gl3").click()
				#time.sleep(10)
				WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "._1gl3")))
			except:
				break

		self.driver.execute_script("window.scrollTo(0, 0);")

		comment_text_element = list(self.driver.find_elements(by=By.CLASS_NAME, value = "_5mdd"))

		comment_text_list = []
		for comment in comment_text_element:
			comment_text_list.append(comment.get_attribute("innerText"))


		username_element = list(self.driver.find_elements(by=By.CLASS_NAME, value = "UFICommentActorName"))

		username_list = []
		for username in username_element:
			username_list.append(username.get_attribute("innerText"))

		comment_timestamp = self.driver.find_elements(by=By.CLASS_NAME, value ="UFISutroCommentTimestamp")

		datetime_list = []

		for timestamp in comment_timestamp:
			comment_datetime = int(timestamp.get_attribute("data-utime"))
			comment_time = datetime.utcfromtimestamp(comment_datetime).strftime('%Y-%m-%d')
			datetime_list.append(comment_time)

		zipped_items = zip(username_list, comment_text_list, datetime_list)
		zipped_list = list(zipped_items)


		url_list = [article_url]

		for comment in zipped_list:
			info = url_list + list(comment)
			comments_list.append(info)

		return comments_list

	def get_comments_from_multiple_articles(self, articles_list):
		"""Returns a list containing all the comments from the articles list"""

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

		comments_df = pd.DataFrame(comments_list, columns = ['URL', 'Display Name', 'Comment Body', 'Date'])
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
