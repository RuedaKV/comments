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

class nyt:
	def __init__(self, api_key):
		"""Initialize api key"""

		self.api_key = api_key

	def article_total_number_comments(self, article_url):
		"""Returns the total number of parent comments from a given article"""

		comment_bucket = "http://api.nytimes.com/svc/community/v3/user-content/url.json?api-key=" + self.api_key + "&offset=0" + "&url=" + article_url
		
		nytimes_request = urllib.request.Request(comment_bucket)
		nytimes_request.add_header('User-Agent', '/Users/rueda/opt/anaconda3/lib/python3.8/urllib/request.py')

		comment_response = urllib.request.urlopen(nytimes_request , timeout=100).read()
		comment_response_dictionary = json.loads(comment_response)

		totalComments = comment_response_dictionary['results']['totalParentCommentsFound']
		totalReplyCommentsFound = comment_response_dictionary['results']['totalReplyCommentsFound']

		num_pages_comments = ceil(totalComments/25)
		return num_pages_comments

	def get_replies_from_comment(self, article_url, comment_sequence):
		"""Returns a list of the replies given a comment sequence"""

		comments_list = []


		try:
			comment_bucket = "http://api.nytimes.com/svc/community/v3/user-content/replies.json?api-key=" + self.api_key + "&offset=0" + "&url=" + article_url + "&commentSequence=" + str(comment_sequence)
			
			nytimes_request = urllib.request.Request(comment_bucket)
			nytimes_request.add_header('User-Agent', '/Users/rueda/opt/anaconda3/lib/python3.8/urllib/request.py')

			comment_response = urllib.request.urlopen(nytimes_request, timeout=100).read()
			comment_response_dictionary = json.loads(comment_response)

			for val in comment_response_dictionary['results']['comments'][0]['replies']:
				createDate = int(val['createDate'])
				createDate = datetime.utcfromtimestamp(createDate).strftime('%Y-%m-%d')

				parentID = val['parentID']
				if parentID == None:
					parentID = "None"

				info = [article_url, parentID, val['commentID'], val['userDisplayName'], val['commentBody'], createDate, val['recommendations'], val['replyCount'], val['editorsSelection']]
				comments_list.append(info)

				if(val['replyCount'] > 0 and val['replyCount'] < 4):	
					for reply in val['replies']:
						createDate = int(reply['createDate'])
						createDate = datetime.utcfromtimestamp(createDate).strftime('%Y-%m-%d')

						parentID = reply['parentID']

						info = [article_url, parentID, reply['commentID'], reply['parentUserDisplayName'], reply['commentBody'], createDate, reply['recommendations'], reply['replyCount'], reply['editorsSelection']]
						comments_list.append(info)

		except urllib.error.HTTPError as e:
			if(e.code == 429):
				time.sleep(5)
				self.get_replies_from_comment(article_url, comment_sequence)

		return comments_list

	def get_one_page(self, article_url, offset):
		"""Returns a single batch of comments from a given article (25 comments)"""

		comments_list = []

		try:
			comment_bucket = "http://api.nytimes.com/svc/community/v3/user-content/url.json?api-key=" + self.api_key + "&offset=" + str(offset) + "&url=" + article_url   
		
			nytimes_request = urllib.request.Request(comment_bucket)
			nytimes_request.add_header('User-Agent', '/Users/rueda/opt/anaconda3/lib/python3.8/urllib/request.py')

			comment_response = urllib.request.urlopen(nytimes_request, timeout=100).read()
			comment_response_dictionary = json.loads(comment_response)

			for val in comment_response_dictionary['results']['comments']:
				createDate = int(val['createDate'])
				createDate = datetime.utcfromtimestamp(createDate).strftime('%Y-%m-%d')

				parentID = val['parentID']
				if parentID == None:
					parentID = "None"

				info = [article_url, parentID, val['commentID'], val['userDisplayName'], val['commentBody'], createDate, val['recommendations'], val['replyCount'], val['editorsSelection']]
				comments_list.append(info)

				if(val['replyCount'] > 0 and val['replyCount'] < 4):	
					for reply in val['replies']:
						createDate = int(reply['createDate'])
						createDate = datetime.utcfromtimestamp(createDate).strftime('%Y-%m-%d')

						parentID = reply['parentID']

						info = [article_url, parentID, reply['commentID'], reply['parentUserDisplayName'], reply['commentBody'], createDate, reply['recommendations'], reply['replyCount'], reply['editorsSelection']]
						comments_list.append(info)

				if(val['replyCount'] > 3):
					comments_list += self.get_replies_from_comment(article_url, val['commentSequence'])

		except urllib.error.HTTPError as e:
			if(e.code == 429):
				time.sleep(5)
				self.get_one_page(article_url, offset)

		return comments_list

	def get_article_comments(self, article_url):
		"""Returns a list of all comments from an article"""

		comments_list = []
		counter = 0
		num_pages_comments = self.article_total_number_comments(article_url)

		while(counter != (num_pages_comments*25)):
			comments_list += self.get_one_page(article_url, counter)
			counter += 25

		return comments_list

	def get_articles_from_spreadsheet(self, spreadsheet_url, sheet_number):
		"""Returns a list of New York Times articles from the spreadsheet"""

		nytimes_list = []

		df = pd.read_html(spreadsheet_url, 
		                  header=1)[sheet_number]
		df.drop(columns='1', inplace=True)

		for index, row in df.iterrows():
			if("nytimes.com" in str(row['Link']) and (str(row['Comments (Y/N)']) == "Yes") and (str(row['Fits Definition']) == "Yes")):
				val = row['Link']

				article = val[:val.index(".html") + len(".html")]
				nytimes_list.append(article)

		return nytimes_list

	def get_comments_from_multiple_articles(self, articles_list):
		"""Returns all the comments from the articles list"""

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

		comments_df = pd.DataFrame(comments_list, columns = ['Link', 'Parent ID', 'Comment ID', 'User Display Name', 'Comment Body', 'Date', 'Recommendations', 'Reply Count', 'Editors Selection'])
		return comments_df

	def sort_by_date(self, data):
		"""Returns a sorted datafrane"""

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

