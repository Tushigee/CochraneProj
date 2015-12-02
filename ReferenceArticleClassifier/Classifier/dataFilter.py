# Purpose of following file is to generate good Data representation 
# from reference downloads

import pymongo as mongo

c = mongo.MongoClient("localhost", 27017)
dbName = "Cochrane"
db = c[dbName]

RefArticles = db["RefArticles"]

CochraneAnalysis = c["CochraneReferenceArticle"]
Data = CochraneAnalysis["Data"]
Train = CochraneAnalysis["Train"]

def submit_comp_data(content, dic, col, includeField):
	global counter
	counter += 1
	submit_sum = {}
	for field in includeField:
		submit_sum[field] = dic[field]
	submit_sum["Content"] = content
	col.insert_one(submit_sum)

includeField = ['Topic', 'ParentLink', '_id', 'SelfLink']

counter = 0


# Only including 
for data in RefArticles.find({"ABSTRA":{"$exists":True},'CONCLUSIONS':{"$exists":True}}):
	content = data['CONCLUSIONS']
	submit_comp_data(content, data, Data, includeField)

# for data in RefArticles.find({"ABSTRA":{"$exists":True},'CONCLUSIONS':{"$exists":False} }):
# 	content = data["ABSTRA"]
# 	submit_comp_data(content, data, Data, includeField)

print "Inserted", counter 
