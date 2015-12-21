# Following code will train model based on it's reference articles 
import pymongo as mongo
import numpy as np 
import cPickle as pickle 
import sklearn.cross_validation as cross_validation
from sklearn.dummy import DummyClassifier as Random
from sklearn.linear_model import LogisticRegression as LR
from sklearn.svm import  SVC
from sknn.mlp import Classifier, Layer
from random import shuffle
from sklearn.preprocessing import normalize

c = mongo.MongoClient("localhost", 27017)

# Tagged articles
CochraneAnalysis = c["CochraneAnalysisArticle"]
Train = CochraneAnalysis["Train"]

# Reference article feature vec
CochraneRefAnalysis = c["CochraneReferenceArticle"]

# Switch between these two databases to use hand picked phrases, or 
DataFeatureVec = CochraneRefAnalysis["DataFeatureVec"] # Non bag of words based
# DataFeatureVec = CochraneRefAnalysis["DataFeatureVecBagOfWords"] # Bag of words feature


# Creating list of tagged article - (Tag, )
# Classifying Yes-ish gave us higher performance as expected

def getTag(tag):
	if (tag == "Y"):
		return 0
	return 1

dataSet = []
found_non_zero = 0

AR_LINK_LIST = []

PARENTID = 0

for train_ar in Train.find():
	# Finding all related reference articles to this article and computing the 
	# vector for entire dataset

	iti = DataFeatureVec.find({"ParentLink": train_ar["Link"]})
	total = iti.count()
	print "Total", total
	#print "Total of", total
	if (total > 5):
		ID_INFO_DIC = {}
		gen_info = [PARENTID, getTag(train_ar["Tag"])]
		ID_INFO_DIC["PARENT_ID"] = PARENTID 
		
		PARENTID += 1 
		
		ID_INFO_DIC["PARENT_LINK"] = train_ar["Link"]
		ID_INFO_DIC["PARENT_TAG"] = train_ar["Tag"]
		ID_INFO_DIC["REF_LINKS"] = []

		found_non_zero += 1
		gen_feat_vec = np.zeros(len(iti[0]['Vector']))
		# # Putting the PARENTI 
		# gen_feat_vec[0] 

		counter_ref = 0

		for ref_arFeat in DataFeatureVec.find({"ParentLink": train_ar["Link"]}):
			ID_INFO_DIC["REF_LINKS"].append((ref_arFeat['SelfLink'], ref_arFeat['Vector']))
			counter_ref += 1
			gen_feat_vec += 1.0*np.asarray(ref_arFeat['Vector'])
		AR_LINK_LIST.append(ID_INFO_DIC)

		gen_feat_vec = (1.0/total)*gen_feat_vec
		# gen_feat_vec = normalize(gen_feat_vec)[0]
		gen_info.extend(gen_feat_vec)
		dataSet.append(gen_info)
pickle.dump(AR_LINK_LIST, open("sumInfoModel.p", "wb"))

dataSet = np.asarray(dataSet)
# print "Data set begining", dataSet
print "Total articles to be considered", found_non_zero

# Doing cross validation
TEST_PORTION = 0.2
testSize  = int(TEST_PORTION*len(dataSet)) 
trainSize = len(dataSet) - testSize

def getDist(train_tag):
	dist = {}
	for tag in train_tag:
		try:
			dist[tag] += 1.0/len(train_tag)
		except KeyError:
			dist[tag] = 1.0/len(train_tag)
	return dist		

def GETRANDOM(data):
	l = []
	for i in xrange(len(data)):
		l.append(np.random.randint(0, 2))
	return l

sumAcc = 0.0
global_wrong_one = 0.0
global_wrong_zero = 0.0
# clf = Random(strategy='uniform')

# clf = Classifier( # 0.55
#     layers=[
#         Layer("Sigmoid", units=25),
#         Layer("Sigmoid", units=20),
#         Layer("Linear")],
#     learning_rate=0.02,
#     n_iter=15)
av_mean = 0.0
itiration = 100
FN = 0.0
FP = 0.0
TP = 0.0
TN = 0.0

def perf_measure(y_actual, y_hat):
	TP = 0.0
	FP = 0.0
	TN = 0.0
	FN = 0.0
	counter = 0
	for i in range(len(y_hat)): 
	    if y_actual[i]==y_hat[i] and y_hat[i] == 1:
	       TP += 1
	for i in range(len(y_hat)): 
	    if y_actual[i]==1 and y_actual[i]!=y_hat[i]:
	       FP += 1
	for i in range(len(y_hat)): 
	    if y_actual[i]==y_hat[i] and y_hat[i]==0:
	       TN += 1
	for i in range(len(y_hat)): 
	    if y_actual[i]==0 and y_actual[i]!=y_hat[i]:
	       FN += 1
	# for i in xrange(len(y_actual)): 
	# 	if int(y_actual[i])==int(y_hat[i]):
	# 		if (y_hat[i] == 1):
	# 			TP += 1
	# 		else:
	# 			TN += 1
	# 	elif (y_actual[i] != y_hat[i]):
	# 		if (y_actual[i] == 1):
	# 			FN += 1
	# 		else:
	# 			FP += 1
	# 	else:
	# 		print "Actual", y_actual[i], y_hat[i]
	return (TP/len(y_hat), FP/len(y_hat), TN/len(y_hat), FN/len(y_hat))

for i in xrange(itiration):
	# clf = Random(strategy='uniform')
	clf = LR() # 0.60 +/- 0.24
	np.random.shuffle(dataSet)
	# print "Dataset", dataSet
	scores = cross_validation.cross_val_score(clf, dataSet[:, 2:], dataSet[:, 1], cv=10)
	print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
	predict = cross_validation.cross_val_predict(clf, dataSet[:, 2:], dataSet[:, 1], cv=10)
	print zip(predict,dataSet[:, 1], dataSet[:, 0])
	dTP, dFP, dTN, dFN = perf_measure(dataSet[:, 1], predict)
	TP += dTP
	FP += dFP
	TN += dTN
	FN += dFN

	
	av_mean += scores.mean()
	

print "Average accuracy is", av_mean/itiration
print "Rate", TP/itiration, FP/itiration, TN/itiration, FN/itiration
 
# Average accuracy is 0.605191666667
# LR clustering based classification 
# LR BAGOFWORD 0.300130769231 0.199869230769 0.305115384615 0.00160769230769  // 0.6051
# LR:          0.281395348837 0.214728682171 0.308837209302 0.00077519379845  // 0.59036996337  # Heuristic
# RANDOM: Rate 0.242015503876 0.254108527132 0.257674418605 0.00186046511628  // 0.497873626374
# ClusterBased 0.446153846153 0.053846153846 0.1            0.00769230769230

# Actual:
# LR BAGOFWORD: 0.301769230769 & 0.194 & 0.306 & 0.198230769231
# LR:           0.304923076923 & 0.206 & 0.293 & 0.195076923077
# Random:       0.252615384615 & 0.250 & 0.249 & 0.247384615385
# BagOfWord:    0.446153846153 0.4   0.1   0.053846153846 // Clustering
# BAGOfWord:    0.230769230769 & 0.169 & 0.330 & 0.269230769230
