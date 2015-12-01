# Purpose of following code is to analyze the data
import operator
import pymongo as mongo

def getDistinctKey(col):
	setOfKeys = reduce(
		lambda all_keys, rec_keys: all_keys | set(rec_keys), 
		map(lambda d: d.keys(), col.find()), 
		set()
	)
	return setOfKeys

def getWordCount(field, itirator):
	dic = {}
	for el in itirator:
		words = el[field].split()
		for word in words:
			try:
				dic[word] += 1
			except KeyError:
				dic[word] = 0
	return dic
def getMaxElement(dic):
	l = list(sorted(dic.iteritems(), key=operator.itemgetter(1), reverse=True))
	return l, sum([a[1] for a in l])
	
# Structure of the database:
# Database Name = "Cochrane"
# Collections inside the database 
# "Links" - Link of each article 
# "ParsedArticles" - Each article with it's own Objectives conclusions etc....
# {"Topic", "SectionLength", "Link"}
# "References" - {"ParentLink": link, "ParentTopic": topic, "RefLinks": []}
# "RefArticles" - {"Topic": topic, "ParentLink": parentLink, "SelfLink": link, other keys for the database}

# Data base set up

c = mongo.MongoClient("localhost", 27017)
dbName = "Cochrane"
db = c[dbName]
Links = db["Links"]
ParsedArticles = db["ParsedArticles"]

################################
#			Links              #
################################

# Getting number of distinct articles 
# 19107 - articles in intersected count

################################
#			ParsedArticles     #
################################

# Total of 3601 articles with keys as follow/ 2798 for non comparion based/ 1968 reference downloaded
# 'Search methods', 'SectionLength', 'Methods', 'Objectives', 
# 'Selection criteria', 'Data collection and analysis', 'Topic', 
# 'Main results', 'Link', 'Background', "Authors' conclusions"
# u'_id',
print "Keys", getDistinctKey(ParsedArticles)

# Getting most common word in the 
fields = ['Objectives', "Authors' conclusions"]
res = {'Objectives': None, "Authors' conclusions": None}
for field in fields:
	itirator = ParsedArticles.find({"SectionLength": {"$gt":6}})
	res[field] = getWordCount(field, itirator)

# Showing maximum first elements
n = 100
for field in fields:
	dic = res[field]
	actRes, summa = getMaxElement(dic)
	print field, len(actRes), summa, actRes[:n]



