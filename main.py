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

	def get_user_tweets(self, username, count=100):
		try:
			status = self.api.user_timeline(screen_name=username, count=count)

			main_twits = {}
			for s in status:
				if s.in_reply_to_status_id is None:
					t = s.__dict__
					t["replies"] = []
					main_twits[s.id] = t
				elif s.in_reply_to_status_id in main_twits.keys():
					main_twits[s.in_reply_to_status_id]["replies"].append(s.__dict__)

			return main_twits
		except Exception as e:
			print(e)
	

def main():
	parser = ArgumentParser()
	parser.add_argument("username", help="username contains user identify")
	
	args = parser.parse_args()

	tu = TwitterUtil()
	status = tu.get_user_tweets(args.username)

	for id, t in status.items():
		print(id, t.get("text"), t.get("replies"))


if __name__ == '__main__':
	main()
