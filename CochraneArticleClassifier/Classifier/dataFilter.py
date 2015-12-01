# Purpose of this code is to filter out the data that is comparison based

# ADDED
import pymongo as mongo

def isRef(validData, collection):
	if collection.find( {'ParentLink': validData["Link"], 'RefLinks' : {"$exists":True}, "$where":'this.RefLinks.length>0'}).count() > 0:
		return True
	return False

c = mongo.MongoClient("localhost", 27017)
dbName = "Cochrane"
db = c[dbName]
ParsedArticles = db["ParsedArticles"]
References = db["References"]

CochraneAnalysis = c["CochraneAnalysisArticle"]
Data =  CochraneAnalysis["Data"]
Train = CochraneAnalysis["Train"]

# Loading valid parsed articles into Data

filteredData = ParsedArticles.find({"SectionLength": {"$gt":6}})
for validData in filteredData:
	if not ("compare" in validData["Objectives"].lower()) and (isRef(validData, References)):
		Data.insert_one(validData)
	else:
		print "Article has no reference", validData["Link"]