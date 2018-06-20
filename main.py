# -*- coding: utf-8 -*-
import tweepy
from configparser import ConfigParser
from argparse import ArgumentParser


class TwitterUtil:
	def __init__(self):
		config = ConfigParser()
		config.read('credentials.cfg')
		self.api = None
		self.credentials = {
			"CONSUMER_KEY": config.get('Twitter', 'CONSUMER_KEY'),
			"CONSUMER_SECRET": config.get('Twitter', 'CONSUMER_SECRET'),
			"ACCESS_TOKEN": config.get('Twitter', 'ACCESS_TOKEN'),
			"ACCESS_TOKEN_SECRET": config.get('Twitter', 'ACCESS_TOKEN_SECRET')
		}

		self.authenticate()

	def authenticate(self):
		auth = tweepy.OAuthHandler(self.credentials["CONSUMER_KEY"], self.credentials["CONSUMER_SECRET"])
		auth.set_access_token(self.credentials["ACCESS_TOKEN"], self.credentials["ACCESS_TOKEN_SECRET"])
		self.api = tweepy.API(auth)

	def find_reply_to_tweet(self, tweet, tweets):
		for item in tweets:
			if item.in_reply_to_status_id is not None and item.in_reply_to_status_id == tweet.id:
				return item

	def fetch_all_replies(self, reply, tweets):
		replies = [reply]
		depht_of_search = 0
		while depht_of_search >= 0:
			parent = replies[depht_of_search]
			child = self.find_reply_to_tweet(parent, tweets)
			if child is None:
				depht_of_search = -1
			else:
				replies.append(child)
				depht_of_search += 1
		return replies

	def format_threads(self, threads):
		threads_formated = []
		for thread in threads:
			new_thread = [thread.get('head').full_text]
			for reply in thread.get('replies'):
				new_thread.append(reply.full_text)
			threads_formated.append(new_thread)
		return threads_formated


	def get_user_tweets(self, username, count=300):
		try:
			status = self.api.user_timeline(screen_name=username, count=count, tweet_mode='extended')
			# Let's fetch all the tweets
			tweets = [s for s in status]
			print("We have {} tweets".format(len(tweets)))
			# Let's filter to the main tweets that may be heads in a thread
			main_twits = list(filter(lambda x: x.in_reply_to_status_id is None, tweets))
			print("We have {} main tweets".format(len(main_twits)))

			# Now we get all the threads that have a reply, forming head:status, replies[status] object
			timeline_threads = []
			for twit in main_twits:
				reply = self.find_reply_to_tweet(twit, tweets)
				if reply is not None:
					new_thread = {'head': twit, 'replies': [reply]}
					timeline_threads.append(new_thread)

			print("We have {} potential threads".format(len(timeline_threads)))
			# Now we try to find the other replies
			for thread in timeline_threads:
				thread['replies'] = self.fetch_all_replies(thread.get('replies')[0], tweets)
			return timeline_threads
		except Exception as e:
			print(e)


def main():
	parser = ArgumentParser()
	parser.add_argument("username", help="username contains user identify")

	args = parser.parse_args()

	tu = TwitterUtil()
	threads = tu.get_user_tweets(args.username)
	formated_threads = tu.format_threads(threads)
	print(formated_threads)

if __name__ == '__main__':
	main()
