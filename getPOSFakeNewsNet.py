import pickle
import re
import postagger
import functions as myFunctions

def vectorizeInput(words, vectorizer):
    input = []
    for index in range(len(words)):
        input.append(postagger.getFeatures(words, index))
    inputVect = vectorizer.transform(input)
    return inputVect

# Carico il modello per ottenere i tag POS
clf = pickle.load(open("modello.sav", 'rb'))
#vectorizer = DictVectorizer(sparse=False)
vectorizer = pickle.load(open("vectorizer.sav", 'rb'))

filenames = ["dataset/politifact.csv", "dataset/gossipcop.csv"]
# Apro ii file contenenti le notizie del dataset FakeNewsNet, politifact e gossipcop
#politifact = open("dataset/politifact.csv", "r")
for filename in filenames:
    file = open(filename, "r", encoding='latin-1', errors="ignore")
    news = dict()
    newsTagged = dict()
    for row in file:
        fields = row.split("\t")
        # ID, Titolo, Sottotitolo, Notizia, True=1 Fake=0
        id = int(fields[0])
        title = fields[1]
        subtitle = fields[2]
        corpus = fields[3]
        true = int(fields[4].strip())
        # Devo levare i campi html dal testo della notizia
        corpus = re.sub("<[^>]*>", "", corpus)
        corpus = re.sub("(https||http)(:\/\/)[A-Za-z0-9.\-/_?=%]*", "", corpus)
        # per levare i link
        # (\w+\.)+(\w+\/\w+(\.\w+)?)
        news[id] = [title, subtitle, corpus, true]
        
    for idNews in news:
        wordsTitle = myFunctions.getWords(news[idNews][0])
        wordsSubtitle = myFunctions.getWords(news[idNews][1])
        wordsCorpus = myFunctions.getWords(news[idNews][2])
        
        taggedNullTitle = myFunctions.getWordsNullTag(wordsTitle)
        taggedNullSubtitle = myFunctions.getWordsNullTag(wordsSubtitle)
        taggedNullCorpus = myFunctions.getWordsNullTag(wordsCorpus)
        
        taggedTitle = []
        taggedSubtitle = []
        taggedCorpus = []
        
        '''for i in range(len(wordsTitle)):
            if wordsTitle[i] == "":
                print(wordsTitle)
        
        for i in range(len(wordsSubtitle)):
            if wordsSubtitle[i] == "":
                print(wordsSubtitle)
        
        for i in range(len(wordsCorpus)):
            if wordsCorpus[i] == "":
                print(wordsCorpus)'''
        
        # Vettorizzo le parole perché il modello accetta vettori come input
        if len(wordsTitle) > 0:
            titleVectorized = vectorizeInput(taggedNullTitle, vectorizer)
            taggedTitle = zip(wordsTitle, clf.predict(titleVectorized))
        
        if len(wordsSubtitle) > 0:
            subtitleVectorized = vectorizeInput(taggedNullSubtitle, vectorizer)
            taggedSubtitle = zip(wordsSubtitle, clf.predict(subtitleVectorized))
        
        if len(wordsCorpus) > 0:
            corpusVectorized = vectorizeInput(taggedNullCorpus, vectorizer)
            taggedCorpus = zip(wordsCorpus, clf.predict(corpusVectorized))
        
        newsTagged[idNews] = [taggedTitle, taggedSubtitle, taggedCorpus]
        
    print(newsTagged)
    pickle.dump(newsTagged, open(filename+".2.pos", "wb"))
    file.close()   
    