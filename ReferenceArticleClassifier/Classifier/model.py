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
DataFeatureVec = CochraneRefAnalysis["DataFeatureVec"]


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
			gen_feat_vec += np.asarray(ref_arFeat['Vector'])
		AR_LINK_LIST.append(ID_INFO_DIC)

		gen_feat_vec = (1.0/total)*gen_feat_vec
		gen_info.extend(gen_feat_vec)
		dataSet.append(gen_info)
pickle.dump(AR_LINK_LIST, open("sumInfoModel.p", "wb"))

dataSet = np.asarray(dataSet)
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
class RandomPredict:
	def fit(x, y):
		pass
	def predict(vector):
		l = []
		for i in xrange(len(vector)):
			l.append(np.random.randint(0, 2))
		return l
	def score(test_feat_vec, test_tag):
		correct = 0.0
		for tag in test_tag:
			if (tag == np.random.randint(0, 2)):
				correct+=1.0
		return correct/len(test_tag)
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
itiration = 1000
FN = 0.0
FP = 0.0
TP = 0.0
TN = 0.0

def perf_measure(y_actual, y_hat):
    TP = 0.0
    FP = 0.0
    TN = 0.0
    FN = 0.0

    for i in range(len(y_hat)): 
        if y_actual[i]==y_hat[i]==1:
           TP += 1
    for i in range(len(y_hat)): 
        if y_actual[i]==1 and y_actual[i]!=y_hat[i]:
           FP += 1
    for i in range(len(y_hat)): 
        if y_actual[i]==y_hat[i]==0:
           TN += 1
    for i in range(len(y_hat)): 
        if y_actual[i]==0 and y_actual[i]!=y_hat[i]:
           FN += 1

	return (TP/len(y_hat), FP/len(y_hat), TN/len(y_hat), FN/len(y_hat))

for i in xrange(itiration):
	# clf = Random(strategy='uniform')
	clf = LR() # 0.60 +/- 0.24
	np.random.shuffle(dataSet)
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
# 
# LR:          0.281395348837 0.214728682171 0.308837209302 0.00077519379845 // 0.59036996337
# RANDOM: Rate 0.242015503876 0.254108527132 0.257674418605 0.00186046511628 //  0.497873626374

# for i in xrange(trainSize):
# 	correct_num = 0
# 	testSet = dataSet[i:i+testSize]
# 	testDic = AR_LINK_LIST[i : i+testSize]

# 	trainSet = np.concatenate((dataSet[:i], dataSet[i+testSize:]), axis=0)
# 	train_tag = trainSet[:, 0]
# 	# print "Train tag", train_tag
# 	# print "Train set", trainSet
# 	train_feat_vec = trainSet[:, 1:]
# 	test_tag = testSet[:, 0]
# 	test_feat_vec = testSet[:, 1:]

# 	# Creating model and training the model 
# 	print "Training model"
	# clf = Classifier(
 #    layers=[
 #        Layer("Sigmoid", units=25),
 #        Layer("Sigmoid", units=20),
 #        Layer("Linear")],
 #    learning_rate=0.02,
 #    n_iter=15)
# 	clf = LR()

# 	clf.fit(train_feat_vec, train_tag)
# 	# Assesing the accuracy of the model
# 	predicted_tag = clf.predict(test_feat_vec)
# 	# Adding all the predicted tags for articles 
# 	# predicted_tag = GETRANDOM(test_feat_vec)
# 	score = clf.score(test_feat_vec, test_tag)
# 	print "Predict", zip(map(lambda x: x["PARENT_ID"], testDic), predicted_tag)
# 	print "Actual", test_tag
# 	print "Score", score
# 	correct = 0.0
# 	wrong_one = 0.0
# 	wrong_zero = 0.0

# 	for i in xrange(len(predicted_tag)):
# 		if predicted_tag[i] == test_tag[i]:
# 			correct += 1
# 		else:
# 			if predicted_tag[i] == 1:
# 				wrong_one += 1
# 			else:
# 				wrong_zero += 1

# 	print "Accuracy was", correct/len(predicted_tag)
# 	print "Dist was", getDist(train_tag)
# 	# print "Counter_num", correct_num
# 	sumAcc += correct/len(predicted_tag)
# 	global_wrong_zero += wrong_zero/(wrong_one+wrong_zero)
# 	global_wrong_one += wrong_one/(wrong_one+wrong_zero)
# 	print "Wrong one", wrong_one/(wrong_one+wrong_zero)
# 	print "Wrong zero", wrong_zero/((wrong_one+wrong_zero))

# print "Average global accuracy is", sumAcc/trainSize
# print "Average wrong one", global_wrong_one/trainSize
# print "Average wrong zero", global_wrong_zero/trainSize

