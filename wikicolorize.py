#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
from lxml import html
import requests
import Algorithmia
from PIL import Image,ImageChops
from io import BytesIO
import pytesseract
import tweepy
import configparser


#Gets a random wikipedia image and context
def get_wikipedia_random(random_wiki_url):
	wiki_image_data = requests.get(random_wiki_url)
	wiki_image_site = html.fromstring(wiki_image_data.content)
	#Gets the media file URL from WikiMedia
	image_url = wiki_image_site.xpath('//div[@class="fullImageLink"]/a/img/@src')	
	#Gets the image description, removing the "English" part
	image_description = wiki_image_site.xpath('//div[contains(@class,\'description\') and contains(@lang,\'en\')]/span/../text()')
	#Gets the redirected URL after WikiMedia's randomization
	media_url = wiki_image_data.url
	print(media_url)
	#Gets the images categories (clearner than description most times, but less descriptive as well)
	image_categories = wiki_image_site.xpath('//div[@class="mw-normal-catlinks"]/ul/li/a/text()') 
	print(image_url)
	#Checks if it is a JPG image
	if image_url and image_url[0] is not None and image_url[0].lower().endswith(('.jpg', '.jpeg')):
		wiki_image = requests.get(image_url[0])
		byte_image = Image.open(BytesIO(wiki_image.content))
		bw_image_path = 'bw.jpg'
		local_path = '/a/web/path/'
		byte_image.save(local_path+bw_image_path,format="JPEG") #Here you have to save the file in a path that can be accessed from the web (because of line 52)
		is_bw = is_bw_image(byte_image)
		if is_bw:
			if not is_document(byte_image):
				colored_image_path = colorize_image(bw_image_path)
				bw_full_path = local_path+bw_image_path
				if colored_image_path:
					if tweet_image(colored_image_path,bw_full_path,media_url,image_description,image_categories):
						return True
					else:
						return False
				else:
					return False
			else:
				return False
		else:
			return False
	else:
		return False

#Colorize Image 
def colorize_image(image_path):
	client = Algorithmia.client('YOUR-ALGORITHMIA-API-KEY')
	algo = client.algo('algorithmiahq/ColorizationDemo/1.1.23') #If you pay for it you may use the non-demo Colorization API 
	input_url = 'http://your-web-host'+image_path #I know this sucks, but it seems like Algorithmia only accepts a URL as input, not an image (image saved in line 29)
	try:
		colored_image = algo.pipe(input_url).result[1]
		filename_colored = save_image(colored_image)
		if filename_colored:
			return filename_colored
		else:
			return False	
	except:
		return False
	
#Tries to OCR a scanned page with Tesseract OCR, if it fails, it probably isn't a document and is more likely to be a photo
def is_document(image):
	try:
		print(pytesseract.image_to_data(image))
		return True
	except Exception as e:
		return False

#Checks if the image is black and white (Code by @Karl K @ https://stackoverflow.com/a/34175631/1284186)
def is_bw_image(im):
	"""
	Check if image is monochrome (1 channel or 3 identical channels)
	"""
	if im.mode not in ("L", "RGB"):
		return False
		raise ValueError("Unsuported image mode")

	if im.mode == "RGB":
		rgb = im.split()
		if ImageChops.difference(rgb[0],rgb[1]).getextrema()[1]!=0: 
			return False
		if ImageChops.difference(rgb[0],rgb[2]).getextrema()[1]!=0: 
			return False
	return True

#Save the colored image in a *.png file
def save_image(imgstring):
	imgdata = base64.b64decode(imgstring)
	filename = 'colored.png'  # I assume you have a way of picking unique filenames
	try:
		with open(filename, 'wb') as f:
			f.write(imgdata)
			f.close()
		return filename
	except:
		return False

#Read configuration file
def read_config():
	config = configparser.ConfigParser()
	config.read('wikicolorize.config.ini')

	return config['twitter']

#Twitter API bureaucracy
def twitter_api():
	config = read_config()
	access_token = config['twitter']['access_token']
	access_token_secret = config['twitter']['access_token_secret']
	consumer_key = config['twitter']['consumer_key']
	consumer_secret = config['twitter']['consumer_secret']

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)
	return api

#Tweets the image with the description and/or category
def tweet_image(colored_image, bw_image, url, description, categories):
	api = twitter_api()
	
	# upload images and get media_ids
	filenames = [bw_image, colored_image]
	media_ids = []
	for filename in filenames:
		 res = api.media_upload(filename)
		 media_ids.append(res.media_id)

	# tweet with multiple images
	api.update_status(status=categories[0]+' '+url, media_ids=media_ids)
	#api.update_with_media(image, status=categories[0]+' '+url)
	return True

if __name__ == "__main__":
	random_wiki_url = 'http://commons.wikimedia.org/wiki/Special:Random/File'
	get_wikipedia_random(random_wiki_url)
	while True:
	  converted = get_wikipedia_random(random_wiki_url)
	  if converted:
	    break
