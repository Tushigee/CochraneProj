# Purpose of the following code is to tag
# Each instance with it's tag

import pymongo as mongo

c = mongo.MongoClient("localhost", 27017)

CochraneAnalysis = c["CochraneAnalysisArticle"]

Data =  CochraneAnalysis["Data"]
Train = CochraneAnalysis["Train"]

CochraneRefAnalysis = c["CochraneReferenceArticle"]
DataRef = CochraneRefAnalysis["Data"]

Y = "Y"
N = "N"
U = "U"
def printAndTag(listOfFields, dic, trainCollection):
	print "============================================"
	for field in listOfFields:
		print field +": " + dic[field]
		print "+++++++++++++"
	# Y - Yes, N - No, U - Unknown, E - Exit
	# YU - from facts it is Y, but it is statistically insignificant
	# UN - from facts it is U, but it is statistically insignificant

	validList = ["Y", "YU", "U", "UN", "N", "YR", "YUR", "UR", "UNR", "NR"]

	tag = raw_input('Please put the tag: ')
	if tag == "E":
		raise Exception()
	elif tag in validList:
		dic["Tag"] = tag
		trainCollection.insert_one(dic)
		print "Inserted the document"
	else:
		print "Please enter correct input"
	

def getTagged(listOfFields, dataCollection, trainCollection, DataRef):
	counter = 0
	for data in dataCollection.find():
		try:
			if (trainCollection.find({"Link": data["Link"]}).count() == 0 and DataRef.find({"ParentLink": data["Link"]}).count() > 5):
				counter += 1	
		except:
			break
	return counter

def getTagged(listOfFields, dataCollection, trainCollection, DataRef):
	for data in dataCollection.find():
		try:
			if (trainCollection.find({"Link": data["Link"]}).count() == 0 and DataRef.find({"ParentLink": data["Link"]}).count() > 10):
				printAndTag(listOfFields, data, trainCollection)
		except:
			break
listOfFields = ['Objectives', "Authors' conclusions"]
getTagged(listOfFields, Data, Train, DataRef)