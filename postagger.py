import nltk
import functions as miefunzioni
import pickle
from sklearn.feature_extraction import DictVectorizer
from sklearn import tree
from sklearn.model_selection import cross_val_score
from joblib import parallel_backend

# Funzione per ottenere le features dalla parole
def getFeatures(taggedSentence, index):
    word = taggedSentence[index][0]
    tag = taggedSentence[index][1]
    
    previousWord = ""
    if index > 0:
        previousWord = taggedSentence[index-1][0]
        previousTag = taggedSentence[index-1][1]
    
    isCapitalized = (word.upper() == word)
    isNumber = False
    try:
        if float(token):
            is_number = True
    except:
        pass
    
    suffix1 = ""
    suffix2 = ""
    suffix3 = ""
    
    if len(word) > 1:
        suffix1 = word[-1]
    if len(word) > 2:
        suffix2 = word[-2:]
    if len(word) > 3:
        suffix3 = word[-3:]
        
    features = { "word": word,
        "wordLowerCase": word.lower(),
        "previousWord": previousWord,
        "suffix1": suffix1,
        "suffix2": suffix2,
        "suffix3": suffix3,
        "isCapitalized": isCapitalized,
        "isNumber": isNumber }
    return features

if __name__ == '__main__':
    # Ottengo le frasi con i pos tags già fatti dal corpus treebank
    taggedSentences = nltk.corpus.treebank.tagged_sents()

    # Ottengo le features e le rendo numeriche (one-hot encoding)
    features = []
    for sentence in taggedSentences:
        for index in range(len(sentence)):
            features.append(getFeatures(sentence, index))
                    
    vectorizer = DictVectorizer(sparse=False)
    x = vectorizer.fit_transform(features)

    print(x.shape)

    # Ottengo i tag delle parole
    y = []
    for sentence in taggedSentences:
        for index in range(len(sentence)):
            y.append(sentence[index][1])

    print(len(y))

    print("Inizio il classificatore\n")      

    clf = tree.DecisionTreeClassifier(criterion='entropy')
    with parallel_backend('threading', n_jobs=-1):
        clf.fit(x,y)

    print ("Finito il classificatore\n")

    fileName = "modello.sav"
    pickle.dump(clf, open(fileName, 'wb'))

    fileName = "vectorizer.sav"
    pickle.dump(vectorizer, open(fileName, 'wb'))

    prova = "Republican attacks on transgendered Americans and the religious fight to keep gender a binary delineation took a turn for the bizarre this week when Virginia Republican Mark Cole filed a bill that would force schools to check the genitals of their students in order to ensure that they are using facilities reserved for their anatomical sex:Local school boards shall develop and implement policies that require every school restroom, locker room, or shower room that is designated for use by a specific gender to solely be used by individuals whose anatomical sex matches such gender designation. Such policies may also provide that a student may, upon request, be granted access, to the extent reasonable, to a single stall restroom or shower, a unisex bathroom, or controlled individual use of a restroom, locker room, or shower."
    print (prova+"\n")
    parole = miefunzioni.getWords(prova)
    paroleTaggateNulle = []
    for parola in parole:
        #print(parola)
        paroleTaggateNulle.append([parola, 'NULL'])
    print(parole)
    input = []
    for indice in range(len(paroleTaggateNulle)):
        input.append(getFeatures(paroleTaggateNulle, indice))
    xTest = vectorizer.transform(input)
    print(zip(parole, clf.predict(xTest)))
        
    # Per vedere come si comporta il modello
    #scores = cross_val_score(clf, X, Y, cv=5)
    #print scores

