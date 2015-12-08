# Purpose of following file is to generate feature vector for each pubmed article using
# heuristic function

import pymongo as mongo
import numpy as np 


c = mongo.MongoClient("localhost", 27017)
dbName = "Cochrane"
db = c[dbName]

RefArticles = db["RefArticles"]

CochraneAnalysis = c["CochraneReferenceArticle"]
Data = CochraneAnalysis["Data"]
DataFeatureVec = CochraneAnalysis["DataFeatureVec"]

# decisive_words = ["did not", "does not", "insufficient", "against", "do not indicate", "did not affect",
# 				  "insufficiently", "not reduce", "does reduce",
# 				  "no evidence", "significantly", "may", "can",
# 				  "improve","improved", "improves", "significant benefit", "benefit", "remain"
# 				  "significantly reduced", "were reduced", "strong evidence", "effective against",
# 				  "effective", "effectively", "support", "better", "effective", "well", "decreased", "unclear", 
# 				  "decrease", "decreasing", "did", "do", "does", "not", "no", "difference", "statistical", "evidence"
# 				  ]

negation_words = ["not", "no"]
action_words = ["did", "do", "does", "should", "may", "will", "must", "can", "might", "was"]

verbs =  ["support", "improve", "indicate", "effect", "affect",
		  "remove", "reduce", "decrease", "benefit", "less", "increase"]

adj_words = ["significant", "potential", "well", "statistical", "strong", "substantial"]
noun_words = ["difference", "evidence", "better", "unclear", "safe"]

decisive_words = negation_words + action_words + adj_words + noun_words

passive_support_words = []

word2index_one = {}
word2index_two = {}
counter = 0

for word in decisive_words:
	if len(word.split()) > 1:
		word2index_two[word] = counter
	else: 
		word2index_one[word] = counter
	counter += 1


# def getFeatureVec_SMART(sentence):
# 	feature_vec = np.zeros(len())
# 	for i in xrange(len(sentence)):
# 		word = sentence[i]



def getFeatureVec(sentence, word2index_one, word2index_two):
	feature_vec = np.zeros(len(word2index_one) + len(word2index_two)+1)
	sentence = sentence.split()
	# Finding all phrases with length 2
	for i in xrange(len(sentence)-2):
		try:
			feature_vec[word2index_two[" ".join(sentence[i:i+2])]] = 1
		except KeyError:
			pass
	# Finding all phrases with length one 
	for i in xrange(len(sentence)):
		try:
			feature_vec[word2index_one[sentence[i]]] = 1
		except KeyError:
			feature_vec
	return feature_vec

for data in Data.find():
	feat_data = {'ParentLink': data['ParentLink'], "SelfLink": data['SelfLink']}
	feature_vec = getFeatureVec(data["Content"][0].encode("utf8"), word2index_one, word2index_two)
	feat_data["Vector"] = list(feature_vec)
	# print feat_data
	DataFeatureVec.insert_one(feat_data)
	
print "Two dic", word2index_two
print "One dic", word2index_one
	
