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
# word2index_one = {}
# word2index_two = {}
# counter = 0

# for word in decisive_words:
# 	if len(word.split()) > 1:
# 		word2index_two[word] = counter
# 	else: 
# 		word2index_one[word] = counter
# 	counter += 1

negation_words = ["not", "no"]
action_words = ["did", "do", "does", "should", "may", "will", "must", 
				"can", "might", "was", "were", "is", "are"]

verbs =  ["support", "improve", "indicate", "effect", "affect",
		  "remove", "reduce", "decrease", "benefit", "achieve"]

adj_words = ["significant", "potential", "well", "statistical", "strong"]
noun_words = ["difference", "evidence", "better", "unclear", "safe", "clear"]
indicative_words = adj_words + noun_words

decisive_words =  action_words + verbs + adj_words + noun_words

passive_support_words = []

word2IndexDic = {}
counter = 0 
for word in decisive_words:
	word2IndexDic[word] = counter
	counter += 1
	word2IndexDic["neg_" + word] = counter 
	counter += 1

def isInSet(word, verbs):
	for verb in verbs:
		if word[:len(verb)].lower() == verb:
			return (True, verb)
	return (False, verb)

def getFeatureVec_SMART(sentence):
	global negation_words
	global action_words
	global verbs
	global adj_words
	global noun_words
	global counter 
	global word2IndexDic
	global indicative_words

	feature_vec = np.zeros(counter)

	# For action word checking only one step ahead for negation
	for i in xrange(0, len(sentence)-1):
		word = sentence[i]
		if (word in action_words):
			if sentence[i+1] in negation_words:
				feature_vec[word2IndexDic["neg_" + word]] = 1
			else:
				feature_vec[word2IndexDic[word]] = 1
	# Checking all verbs checking only previous one word
	for i in xrange(2, len(sentence)):
		word = sentence[i]
		dec, verb = isInSet(word, verbs)
		if (dec):
			if (sentence[i-1] in negation_words) or (sentence[i-2] in negation_words):
				feature_vec[word2IndexDic["neg_" + verb]] = 1
			else:
				feature_vec[word2IndexDic[verb]] = 1
	# Checking all 
	for i in xrange(2, len(sentence) - 2):
		word = sentence[i]
		dec, verb = isInSet(word, indicative_words)
		if (dec):
			if (sentence[i-1] in negation_words) or (sentence[i-2] in negation_words):
				feature_vec[word2IndexDic["neg_" + verb]] = 1
			else:
				feature_vec[word2IndexDic[verb]] = 1
	return feature_vec

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
	# feature_vec = getFeatureVec(data["Content"][0].encode("utf8"), word2index_one, word2index_two)
	feature_vec = getFeatureVec_SMART(data["Content"][0].encode("utf8").split())
	feat_data["Vector"] = list(feature_vec)
	# print feat_data
	DataFeatureVec.insert_one(feat_data)
print "Translatoin", word2IndexDic	
# print "Two dic", word2index_two
# print "One dic", word2index_one
	
