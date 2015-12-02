# Following code will train model based on it's reference articles 
import pymongo as mongo
import numpy as np 
from sklearn.svm import SVC

c = mongo.MongoClient("localhost", 27017)

# Tagged articles
CochraneAnalysis = c["CochraneAnalysisArticle"]
Train = CochraneAnalysis["Train"]

# Reference article feature vec
CochraneAnalysis = c["CochraneReferenceArticle"]
DataFeatureVec = CochraneAnalysis["DataFeatureVec"]


# Creating list of tagged article - (Tag, )

def getTag(tag):
	if (tag == "Y"):
		return 0
	return 1

dataSet = []
found_non_zero = 0

for train_ar in Train.find():
	gen_info = [getTag(train_ar["Tag"])]
	# Finding all related reference articles to this article and computing the 
	# vector for entire dataset

	iti = DataFeatureVec.find({"ParentLink": train_ar["Link"]})
	total = iti.count()
	#print "Total of", total
	if (total > 10):
		found_non_zero += 1

	if (total > 0):
		gen_feat_vec = np.zeros(len(iti[0]['Vector']))
		
		for ref_arFeat in DataFeatureVec.find({"ParentLink": train_ar["Link"]}):
			gen_feat_vec += np.asarray(ref_arFeat['Vector'])
		gen_feat_vec = (1.0/total)*gen_feat_vec
		gen_info.extend(gen_feat_vec)
		dataSet.append(gen_info)

dataSet = np.asarray(dataSet)
print "Total articles to be considered", found_non_zero

# Doing cross validation
TEST_PORTION = 0.1
testSize  = int(TEST_PORTION*len(dataSet)) 
trainSize = len(dataSet) - testSize

sumAcc = 0.0
for i in xrange(trainSize):
	testSet = dataSet[i:i+testSize]
	trainSet = np.concatenate((dataSet[:i], dataSet[i+testSize:]), axis=0)
	train_tag = trainSet[:, 0]
	# print "Train tag", train_tag
	# print "Train set", trainSet
	train_feat_vec = trainSet[:, 1:]
	test_tag = testSet[:, 0]
	test_feat_vec = testSet[:, 1:]

	# Creating model and training the model 
	print "Training model"
	clf = SVC()
	clf.fit(train_feat_vec, train_tag)
	# Assesing the accuracy of the model
	predicted_tag = clf.predict(test_feat_vec)
	correct = 0.0
	for i in xrange(len(predicted_tag)):
		if predicted_tag[i] == test_tag[i]:
			correct += 1
	print "Accuracy was", correct/len(predicted_tag)
	sumAcc += correct/len(predicted_tag)

print "Average global accuracy is", sumAcc/trainSize

