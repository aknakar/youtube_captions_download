"""
A module to crawl through each video on a YouTube channel and store the auto-generated captions for each video in a dictionary.
"""


from selenium import webdriver
import re
import time
import csv
from selenium.webdriver.chrome.options import Options
from pytube import YouTube

# A function that opens a headless driver

def create_channel_list():
	channel_list = []
	channel = input("Enter a YouTube channel URL. Enter nothing to quit: ")
	channel_list.append(channel)
	while channel != '':
		channel = input("Enter a YouTube channel URL. Enter nothing to quit: ")
		if channel != '': channel_list.append(channel)
	return channel_list
	

def create_headless_driver(channel):
	# Opens headless browser driver
	chrome_options = Options()
	chrome_options.add_argument("--headless")
	driver = webdriver.Chrome(options=chrome_options)
	driver.get(channel + "/videos")
	return driver

# A function that scrolls to the bottom of the webpage

def scroll_to_bottom(driver):

    old_position = 0
    new_position = None

    while new_position != old_position:
        # Get old scroll position
        old_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                 " window.pageYOffset : (document.documentElement ||"
                 " document.body.parentNode || document.body);"))
        # Sleep and Scroll
        time.sleep(3)
        driver.execute_script((
                "var scrollingElement = (document.scrollingElement ||"
                " document.body);scrollingElement.scrollTop ="
                " scrollingElement.scrollHeight;"))
        # Get new position
        new_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                 " window.pageYOffset : (document.documentElement ||"
                 " document.body.parentNode || document.body);"))

# Function to download all captions for all videos on the channel 

def download_captions(driver):
	# Finds all links to videos on the page.
	links = driver.find_elements_by_xpath('//*[@id="video-title"]')

	# What do we want to store in the vid_info dictionary? 
	videos = []

	# Takes all links and stores the auto-generated captions for each video in vid_info.
	for link in links:
		try:
			vid_info = {}
			tmp = YouTube(link.get_attribute('href'))
			vid_info['author'] = tmp.author
			vid_info['title'] = tmp.title
			vid_info['date'] = tmp.publish_date
			vid_info['link'] = (link.get_attribute('href'))
			vid_info['captions'] = " ".join(re.findall("^.*[a-zA-Z]", tmp.captions['a.en'].generate_srt_captions(), re.MULTILINE))
			videos.append(vid_info)
			print(vid_info['link'])	#used to debug
		except:
			continue

	return videos


def create_csv(list):
	keys = list[0].keys()
	with open('youtube.csv', 'w', newline='') as output_file:
		writer = csv.DictWriter(output_file, keys)	
		writer.writeheader()
		writer.writerows(list)

def master_list():
	channel_list = create_channel_list()
	videos = []
	for channel in channel_list:
		driver = create_headless_driver(channel)
		scroll_to_bottom(driver)
		videos += download_captions(driver)
	return videos


create_csv(master_list())