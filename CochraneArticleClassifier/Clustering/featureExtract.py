# Purpose of following code is to convert entire "Authors Conclusion Section into 
import cPickle as pickle
import pymongo as mongo
import numpy as np
import operator 
from sklearn.cluster import KMeans

c = mongo.MongoClient("localhost", 27017)

CochraneAnalysis = c["CochraneAnalysisArticle"]
Data =  CochraneAnalysis["Data"]

wordCountDic = {}
special_char = [".", ","]

for data in Data.find():
	words = data["Authors' conclusions"].split()
	for sentence_word in words:
		# Removing special characters
		word = sentence_word
		if word[-1] in special_char:
			word = word[:-1]
		try:
			wordCountDic[word] += 1
		except KeyError:
			wordCountDic[word] = 1

l = list(sorted(wordCountDic.iteritems(), key=operator.itemgetter(1), reverse=True))
# Trimming out a lot of repeated, and least repeated words
l = [i[0] for i in l if (i[1] > 50 and 1800> i[1])]
word_dic_index = {}
counter = 0
for word in l:
	word_dic_index[word] = counter 
	counter += 1  

data_matrix = []
id_map = []

# Creating feature vector for each article
for data in Data.find():
	feature_vec = np.zeros(len(l))
	words = data["Authors' conclusions"].split()

	for sentence_word in words:
		# Removing special characters
		word = sentence_word
		if word[-1] in special_char:
			word = word[:-1]
		try:
			feature_vec[word_dic_index[word]] = 1
		except KeyError:
			pass
	data_matrix.append(feature_vec)
	id_map.append(data["_id"])

# Clustering all the data points
model = KMeans(n_clusters=3)
model.fit(data_matrix)

label_id_list = zip(id_map, model.labels_)
pickle.dump(label_id_list, open("modelLabel.p", "wb"))

labelMatches = [0, 1, 2] # 0 - No  -478, 1 - Unknown - 687, 2 - 488
counter = 0 
for labelMatch in labelMatches:
	print "Following is LABEL:", labelMatch
	for id_tag, label in label_id_list:
		if label == labelMatch:
			counter += 1
			print Data.find({"_id":id_tag})[0]["Authors' conclusions"].encode("utf8")
			print "+++++++++++++++++++++++++++++++++++++++"
	print "TOTAL", labelMatch, counter





