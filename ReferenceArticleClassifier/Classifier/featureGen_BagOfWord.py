# Purpose of following file is to generate feature vector for each pubmed article using
# heuristic function

import pymongo as mongo
import numpy as np 
import operator 

c = mongo.MongoClient("localhost", 27017)
dbName = "Cochrane"
db = c[dbName]

RefArticles = db["RefArticles"]

CochraneAnalysis = c["CochraneReferenceArticle"]
Data = CochraneAnalysis["Data"]
DataFeatureVec = CochraneAnalysis["DataFeatureVecBagOfWords"]

def getWordCount(field, itirator):
	dic = {}
	for el in itirator:
		words = el[field][0].split()
		for word in words:
			try:
				dic[word] += 1
			except KeyError:
				dic[word] = 0
	return dic

def getMaxElement(dic):
	l = list(sorted(dic.iteritems(), key=operator.itemgetter(1), reverse=True))
	return l, sum([a[1] for a in l])

def getFeatureVec(sentence, word2IndexDic):
	feature_vec = np.zeros(len(word2IndexDic))
	sentence = sentence.split()
	for i in xrange(len(sentence)):
		word = sentence[i]
		try:
			feature_vec[word2IndexDic[word]] = 1
		except KeyError:
			pass
	return feature_vec

wordCountDic = None
itirator = Data.find()
# Finding all the words 
wordCountDic = getWordCount("Content", itirator)

# Showing maximum first elements
lower = 15 # Excluding first 15 most common used words
actRes, summa = getMaxElement(wordCountDic)
actRes = actRes[lower:]
counter = 0
lowLimit = 200 # words only appeared more than 200 times are used

word2IndexDic = {}

for word, number in actRes:
	if number > lowLimit:
		word2IndexDic[word] = counter
		counter += 1

print "Total of words:", len(word2IndexDic)

# Generating feature vector for all sentences

for data in Data.find():
	feat_data = {'ParentLink': data['ParentLink'], "SelfLink": data['SelfLink']}
	feature_vec = getFeatureVec(data["Content"][0].encode("utf8"), word2IndexDic)
	feat_data["Vector"] = list(feature_vec)
	DataFeatureVec.insert_one(feat_data)

	
