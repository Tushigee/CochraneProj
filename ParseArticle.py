# The purpose of following code is to scrape information about article for given link

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time 

import cPickle as p

import pymongo as mongo

# DB srtucture:
# Links has all the articles tagged by its 

def getReferenceLink(driver, link, topic, references):
	return None

def parseArticle(driver, link, collection, topic):
	if (collection.find({"Link": link}).count() == 0):
		driver.get(link)
		# time.sleep(5)
		WebDriverWait(driver, 3).until(
			EC.presence_of_element_located((By.CLASS_NAME, "article-section__content"))
		)
		# Waiting until page is loaded
		mainSummary = driver.find_element_by_class_name("article-section__content")
		sections = mainSummary.find_elements_by_class_name("article-body-section")
		article = {"Topic": topic, "Link":link}
		print "Added total", len(sections)
		article["SectionLength"] = len(sections)
		for section in sections:
			key = section.find_element_by_tag_name("h3")
			body = section.find_element_by_tag_name("p")
			article[key.text] = body.text
		collection.insert_one(article)
# Setting up database  	

c = mongo.MongoClient("localhost", 27017)
dbName = "Cochrane"
db = c[dbName]
linkCol = db["Links"]

collectionArticle = db["ParsedArticles"]
references = db["References"]
profile = webdriver.FirefoxProfile()
profile.set_preference("javascript.enabled", False);
driver = webdriver.Firefox(profile)
# Wait 10 seconds
# driver.implicitly_wait(3)
validTopic = ["Lungs & airways",
		  "Mental health", "Methodology", "Neonatal care", "Neurology",
		  "Orthopaedics & trauma", "Pain & anaesthesia", "Pregnancy & childbirth",
		  "Public health", "Rheumatology", "Skin disorders", "Tobacco, drugs & alcohol", 
		  "Urology", "Wounds"]
for topic in linkCol.distinct("Topic"):
	if topic in validTopic:
		setOfLink = set([link["link"] for link in linkCol.find({"Topic":topic})])
		for link in setOfLink:
			try:
				parseArticle(driver, link, collectionArticle, topic)
			except:
				print "Failed at", topic, link
			# getReferenceLink(driver, link, topic, references)