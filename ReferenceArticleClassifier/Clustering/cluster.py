# The purpose of following file is to cluster reference articles feature vector

import pymongo as mongo
import numpy as np 
import cPickle as p
from sklearn.cluster import KMeans

c = mongo.MongoClient("localhost", 27017)
dbName = "Cochrane"
db = c[dbName]

RefArticles = db["RefArticles"]

CochraneAnalysis = c["CochraneReferenceArticle"]
Data = CochraneAnalysis["Data"]
DataFeatureVec = CochraneAnalysis["DataFeatureVec"]

data_matrix = []
link_matrix = []
for feat_vec in DataFeatureVec.find():
	data_matrix.append(np.asarray(feat_vec["Vector"]))
	link_matrix.append(feat_vec["SelfLink"])

model = KMeans(n_clusters=2)
model.fit(data_matrix)

label_id_list = zip(link_matrix, model.labels_)
p.dump(label_id_list, open("clusterResult.p", "wb"))

