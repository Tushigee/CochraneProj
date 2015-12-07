# Purpose of following code is to generate word embeddings for similar topic words

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


from gensim import corpora, models, similarities
dictionary = corpora.Dictionary.load('freqWords.dict')
corpus = corpora.MmCorpus('refCorpus.mm')

# model = models.ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=2)
model = models.LsiModel(corpus, id2word=dictionary, num_topics=3) 

corpus_model = model[corpus]

print model.print_topics(10)

print "Modeling"
documents = []
for line in open("refArticleText.txt"):
	documents.append(line)

for i in xrange(len(corpus_model)):
	print "ACTUAL TEXT", documents[i]
	print "Prediction", corpus_model[i]
	print "++++++++++++++++++++++++++++++"

