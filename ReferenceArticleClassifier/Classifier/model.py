# Following code will train model based on it's reference articles 
import pymongo as mongo
import numpy as np 
import cPickle as pickle 

from sklearn.linear_model import LogisticRegression as LR
from sknn.mlp import Classifier, Layer

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
	gen_info = [getTag(train_ar["Tag"])]
	# Finding all related reference articles to this article and computing the 
	# vector for entire dataset

	iti = DataFeatureVec.find({"ParentLink": train_ar["Link"]})
	total = iti.count()

	#print "Total of", total
	if (total > 5):
		ID_INFO_DIC = {}
		PARENTID += 1 
		ID_INFO_DIC["PARENT_ID"] = PARENTID 
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

		# gen_feat_vec = (1.0/total)*gen_feat_vec
		gen_feat_vec = (1.0/(total))*gen_feat_vec
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

sumAcc = 0.0
global_wrong_one = 0.0
global_wrong_zero = 0.0


for i in xrange(trainSize):
	correct_num = 0
	testSet = dataSet[i:i+testSize]
	testDic = AR_LINK_LIST[i : i+testSize]

	trainSet = np.concatenate((dataSet[:i], dataSet[i+testSize:]), axis=0)
	train_tag = trainSet[:, 0]
	# print "Train tag", train_tag
	# print "Train set", trainSet
	train_feat_vec = trainSet[:, 1:]
	test_tag = testSet[:, 0]
	test_feat_vec = testSet[:, 1:]

	# Creating model and training the model 
	print "Training model"
	clf = Classifier(
    layers=[
        Layer("Sigmoid", units=25),
        Layer("Sigmoid", units=20),
        Layer("Linear")],
    learning_rate=0.02,
    n_iter=15)
	
	clf.fit(train_feat_vec, train_tag)
	# Assesing the accuracy of the model
	predicted_tag = clf.predict(test_feat_vec)
	# Adding all the predicted tags for articles 
	# predicted_tag = GETRANDOM(test_feat_vec)
	# score = clf.score(test_feat_vec, test_tag)
	print "Predict", zip(map(lambda x: x["PARENT_ID"], testDic), predicted_tag)
	print "Actual", test_tag
	# print "Score", score
	correct = 0.0
	wrong_one = 0.0
	wrong_zero = 0.0

	for i in xrange(len(predicted_tag)):
		if predicted_tag[i] == test_tag[i]:
			correct += 1
		else:
			if predicted_tag[i] == 1:
				wrong_one += 1
			else:
				wrong_zero += 1

	print "Accuracy was", correct/len(predicted_tag)
	print "Dist was", getDist(train_tag)
	# print "Counter_num", correct_num
	sumAcc += correct/len(predicted_tag)
	global_wrong_zero += wrong_zero/len(predicted_tag)
	global_wrong_one += wrong_one/len(predicted_tag)

print "Average global accuracy is", sumAcc/trainSize
print "Average wrong one", global_wrong_one/trainSize
print "Average wrong zero", global_wrong_zero/trainSize

