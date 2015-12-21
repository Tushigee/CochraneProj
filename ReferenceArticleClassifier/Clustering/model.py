import cPickle as p
import pymongo as mongo

c = mongo.MongoClient("localhost", 27017)

# Tagged articles
CochraneAnalysis = c["CochraneAnalysisArticle"]
Train = CochraneAnalysis["Train"]

# Getting all reference articles tag as well 
CochraneRefAnalysis = c["CochraneReferenceArticle"]
DataClusterResult = CochraneRefAnalysis["ClusterResult"]

# for each article finding the reference articles and taking majority vote
prediction = []
actual = []
# def perf_measure(y_actual, y_hat):
def perf_measure(y_actual, y_hat):
	TP = 0.0
	FP = 0.0
	TN = 0.0
	FN = 0.0
	counter = 0
	for i in xrange(len(y_actual)): 
		counter += 1
		if int(y_actual[i])==int(y_hat[i]):
			if (y_hat[i] == 1):
				TP += 1
			else:
				TN += 1
		elif (y_actual[i] != y_hat[i]):
			if (y_actual[i] == 1):
				FN += 1
			else:
				FP += 1
		else:
			print "Actual", y_actual[i], y_hat[i]
	return (TP/len(y_hat), FP/len(y_hat), TN/len(y_hat), FN/len(y_hat))

	
def getTag(tag):
	if (tag == "Y"):
		return 0
	return 1

for ar in Train.find():
	vote = [0.0, 0.0]
	par_link = ar["Link"]
	iti = DataClusterResult.find({"ParentLink": par_link})
	if iti.count() > 5:
		for ref_ar in iti:
			vote[int(ref_ar["ClusterTag"])] += 1
		print vote
		prediction.append(int(vote[0] < 0.2*vote[1]))
		actual.append(getTag(ar["Tag"]))
print "Predicted", len(prediction)
print prediction
print "Actual", len(actual)
print actual
print perf_measure(actual, prediction)


	