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

def getReferenceLink(driver, link, topic, references, collectionArticle):
	if (collectionArticle.find({"Link":link}).count() > 0 and references.find({"ParentLink": link}).count() == 0):
		driver.get(link)
		WebDriverWait(driver, 3).until(
			EC.presence_of_element_located((By.CLASS_NAME, "article-section__content"))
		)
		refCol = {"ParentLink": link, "ParentTopic": topic}
		l = driver.find_element_by_link_text('References')
		l.click()
		time.sleep(1)
		referenceLinkList = driver.find_elements_by_link_text('PubMed')
		print "Ref link downloaded", len(referenceLinkList)
		refCol["RefLinks"] = [refEl.get_attribute("href") for refEl in referenceLinkList]
		references.insert_one(refCol)

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
driver = webdriver.Firefox()

# Wait 10 seconds
# driver.implicitly_wait(3)

for topic in linkCol.distinct("Topic"):
	setOfLink = set([link["link"] for link in linkCol.find({"Topic":topic})])
	for link in setOfLink:
		if (link != "http://onlinelibrary.wiley.com/enhanced/doi/10.1002/14651858.CD007566.pub2"):
			try:
				if (references.find({"ParentLink": link}).count() == 0):
					# parseArticle(driver, link, collectionArticle, topic)
					getReferenceLink(driver, link, topic, references, collectionArticle)
			except:
				print "Failed at", topic, link
		else:
			print "Forbidden link found"
		# getReferenceLink(driver, link, topic, references)