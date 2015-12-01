# The purpose of following code is to train the model based on 
# the classifier labeled by hand
import pymongo as mongo
from tgrocery import Grocery

c = mongo.MongoClient("localhost", 27017)
CochraneAnalysis = c["CochraneAnalysisArticle"]
Train = CochraneAnalysis["Train"]
Data =  CochraneAnalysis["Data"]
PredictedLabels = CochraneAnalysis["PredictedLabels"]

x = ["Y", "YU", "U", "UN", "N", "YR", "YUR", "UR", "UNR", "NR"]
def getTag(tag):
	return tag[0]

grocery = Grocery('sample')

train_src = []

for data in Train.find():
	label = getTag(data["Tag"])
	text = data["Authors' conclusions"]
	train_src.append((label, text))

# Preparing training data from hand labeled classfiers
grocery.train(train_src)
grocery.save()

for data in Data.find():
	pred_label = grocery.predict(data["Authors' conclusions"])
	data["PredictedLabel"] = pred_label
	PredictedLabels.insert_one(data)


