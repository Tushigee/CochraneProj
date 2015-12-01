# Purpose of the following code is to download references articles body
import urllib2
import pymongo as mongo
import sys
from bs4 import BeautifulSoup

c = mongo.MongoClient("localhost", 27017)
dbName = "Cochrane"
db = c[dbName]
refArticle = db["RefArticles"]

def flatten_recursive(notices):
	# print "NOTICE", notices
	try:
		length = len(notices.contents)
		string = notices.text
	except AttributeError:
		length = 1
		string = notices
	if (length == 1):
		return [string]
	else:
		try:
			l = [notices.contents[0].text]
		except AttributeError:
			l = [notices.contents[0]]
		for content in notices.contents[1]:
			l.extend(flatten_recursive(content))
		return l

def flatten(notices):
	flattenList = flatten_recursive(notices)
	# Eliminating abstract
	flattenList[0] = flattenList[0].upper()
	return flattenList

def parseRefArticle(link, parentLink, refArticle, topic):
	response = urllib2.urlopen(link)
	html = response.read()
	soup = BeautifulSoup(html, 'html.parser')
	err = soup.find("div", {"class" : "err"})
	notices = soup.find("div", {"class" : "abstr"})
	referencedArticle = {"Topic": topic, "ParentLink": parentLink, "SelfLink": link}
	
	if (notices != None):
		contents = flatten(notices)
		isKey = False
		key = None
		for i in xrange(len(contents)):
			if contents[i].isupper():
				isKey = True
				key = contents[i][:-2]
				referencedArticle[key] = []
			else:
				referencedArticle[key].append(contents[i])

		print "Inserted", len(contents)
	else:
		print "Notice empty at", link

	if err != None:
		referencedArticle["Error"] = str(err)
		print "Error Reported", link, err
	print "Just Inserted", referencedArticle
	refArticle.insert_one(referencedArticle)
	
ref = db["References"]
corruptRef = db["CorruptReferences"]

articles = ref.find({"RefLinks" : {"$exists":True}, "$where":'this.RefLinks.length>0'})
forbidWord = "AMBIGUOUS"
forbidWord1 = "Can't"
# Downloading all referenced articles from pubMed
for article in articles:
	parentLink = article["ParentLink"]
	topic = article["ParentTopic"]
	for refLink in article["RefLinks"]:
		try:
			if (refArticle.find({"SelfLink": refLink}).count() == 0 and (not forbidWord in refLink) and (not forbidWord1 in refLink)):
				print "RefLink", refLink
				parseRefArticle(refLink, parentLink, refArticle, topic)
		except: # catch *all* exceptions
			e = sys.exc_info()[0]
			print "<p>Error: %s</p>" % e
			error = {"link": refLink}
			error["error"] = str(e) 
			corruptRef.insert_one(error)