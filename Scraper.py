# Purpose of following code is to aggregate all links
# on cochrane database that has Triple - YES/NO/Maybe answers

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time 

import cPickle as p

import pymongo as mongo

def getLink(el):
	heading = el.find_element_by_class_name("results-block__description-heading")
	return heading.find_element_by_class_name("results-block__link").get_attribute("href")

def getLinksSinglePage(collection, driver):
	# Getting list of all articles
	WebDriverWait(driver, 1).until(
		EC.presence_of_element_located((By.CLASS_NAME, "results-block__article"))
	)

	articleList = driver.find_elements_by_class_name("results-block__article")
	for i in xrange(len(articleList)):
		info = {"Topic": topic}
		try:
			info["link"] = getLink(articleList[i])
			# print "Saved file with link", info["link"]
			collection.insert_one(info)
		except:
			print "Failed to save at", i

def getLinks(topic, collection, driver):
	startPage = "http://www.cochranelibrary.com/home/topic-and-review-group-list.html?page=topic"
	# Clicking on given topic
	driver.get(startPage)
	# Loading the page
	driver.find_element_by_link_text(topic).click()
	# Waiting until page is loaded
	numberSelector = WebDriverWait(driver, 1).until(
        EC.presence_of_element_located((By.ID, "results_per_page_top"))
    )

	select = Select(numberSelector)
	# Loading 100 element on the page
	select.select_by_visible_text("100")
	time.sleep(3)

	# Gettin page number 
	pageNext = driver.find_element_by_class_name("results-block__pagination-list")
	listPage = pageNext.find_elements_by_tag_name("li")

	for i in range(len(listPage)-1):
		getLinksSinglePage(collection, driver)

		pageNext = driver.find_element_by_class_name("results-block__pagination-list")
		listPage = pageNext.find_elements_by_tag_name("li")

		# Click on next button
		listPage[-1].click()
		time.sleep(10)

c = mongo.MongoClient("localhost", 27017)
dbName = "Cochrane"
db = c[dbName]

driver = webdriver.Firefox()
# Topics to be downloaded from cochrane database
colName = "Links"
col = db[colName]

topics = ["Allergy & intolerance", "Blood disorders", "Cancer", 
		  "Child health", "Complementary & alternative medicine", 
		  "Consumer & communication strategies", "Dentistry & oral health",
		  "Developmental, psychosocial & learning problems",
		  "Diagnosis", "Ear, nose & throat", "Effective practice & health systems",
		  "Endocrine & metabolic", "Eyes & vision", "Gastroenterology", "Genetic disorders",
		  "Gynaecology", "Health & safety at work", "Heart & circulation",
		  "Infectious disease", "Kidney disease", "Lungs & airways",
		  "Mental health", "Methodology", "Neonatal care", "Neurology",
		  "Orthopaedics & trauma", "Pain & anaesthesia", "Pregnancy & childbirth",
		  "Public health", "Rheumatology", "Skin disorders", "Tobacco, drugs & alcohol", 
		  "Urology", "Wounds"]

for topic in topics:
	try:
		getLinks(topic, col, driver)
	except:
		print "Failed at topic", topic



