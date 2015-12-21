Cochrane Review Classification
=================

Author
-------------------
Battushig Myanganbayar

Advisors 
--------------
Prof. Regina Barzilay
Franck Dernoncourt 

All other known bugs, improvements, and questions can be sent to btushig@mit.edu



File Directory
--------------
Following is the list of files in the project, and their relevant roles:


> dataAnalyzer.py - Methods provided to give analytics about collected Cochrane Review Articles. In comments section, you can find read structural description of different collections. 

> ParseArticle.py - Given link of Cochrane Review Article, methods provided will parse the article, and save it as a dictionary specified in comments section to database. This file parses all Cochrane Review Articles included in Links collection. 

> RefDownload.py - Downloads all reference links for given Cochrane Review Article. This file scrapes all Cochrane Review Articles' references in .

> Scraper.py - Scrapes entire article links from Cochrane Review for given topics specified in the list. 

> .CochraneArticleClassifier - This folder includes the experimental code to classify Cochrane Review Article based on supervised data. 

>> trainTag.py - Running this script will start interactive shell process to handle label Cochrane Review Article as having negative, or positive polarity. 

> .ReferenceArticleClassifier - This folder includes code related to two main algorithmic approaches taken for classificatoin task.

>> Classifier - This folder includes code to extract feature vector from references articles, represent Cochrane Review Article as a feature vector, train and evaluate accuracy of LR model. 

>>> dataFilter.py - This script filters noisy data on RefArticles collection, and creates Data, and Train data collectoins with filtered data

>>> featureGen.py - Converts Reference articles on Data to its feature vector form using hand crafted phrases
>>> featureGen_BagOfWord.py - Converts Reference articles on Data to its feature vector form using bag of words as a feature

>>> model.py - Generates feature representation of Cochrane Review article by combining feature vector from references. 

>>> sumInfoModel.p - Dictionary in pickle format to see the quality of the prediction. 

>> Clustering - This folder includes code to extract feature vector from references articles, and cluster them to represent their polarity. 

>>> cluster.py - Given feature vectors of reference articles on Data collection, this script will run k++ clustering with 2 clusters, and tag every reference with its corresponding cluster.

>>> clusterResult.p - This file will include reference article link, and corresponding tag. By visually inspecting this file, can decide which cluster tag correspond to what. 

>>> model.py - Takes majority vote from reference articles, and predict polarity of parent Cochrane Review Article. 

>> WordEmbeddings - Experimental code to improve accuracy
of classification 

How to run program
------------------

Install all required packages: MongoDB, Scikit-learn

Once set up is done, read through file directory to perform neccessary experiments. 

Database Access
----------------
This project runs in MongoDB. Please, contact with btushig@mit.edu to get an access to Cochrane Review Databases used in this project.



