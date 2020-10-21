# Libreria per effettuare operazioni sul testo
# Le frequenze sono standardizzate TF-IDF per essere indipendenti dalla lunghezza del testo
# Il file aperto contiene in ogni riga una notizia diversa effettuato fuori di qui 

import re
import math

# Funzione che dato un array di testi scompone ciasccuno di esso in un array di frasi ( sequenza di parole che termina con un simbolo di punteggiatura come . ? !)
# ho le parole, una frase è fino ad un . ? !
def getSentences(words):
    #frasi = []
    #sentencesTexts = []
    sentences = []
    sentence = []
    
    for index in range(len(words)):
        word = words[index]
        sentence.append(word)
        if word in ['!', '.', '?'] or index==len(words)-1:
            sentences.append(sentence)
            #print("Trovato simbolo per terminare la frase o ultima parola")
            #print(sentence)
            sentence = []
    #print(sentences)
    return sentences
    
# Funzione che dato un array di testi ricava le singole parole (?:[A-Z]\.)+|\w+(?:-\w+)*|\$?\d+(?:\.\d+)?%?|\.\.\.|[][.,;"'?():-_]
# (?:[A-Z]\.)+|\w+(?:-\w+)*|\$?\d+(?:\.\d+)?%?|\.\.\.|[&.,;"'?():-_]
#[\w]+'t|(?:[A-Z]\.)+|\w+(?:-\w+)*|\$?\d+(?:\.\d+)?%?|\.\.\.|[&.,;"'?():-_]   questa prende anche aren't couldn't come unica parola
# [\w]+'t|(?:[A-Z]\.)+|\d+(?:\.\d+)?|\w+(?:-\w+)*|\.\.\.|[&.,€£;%\$\"'?():-_] 
def getWords(text):
    words = re.findall(r"[\w]+'t|(?:[A-Z]\.)+|\d+(?:\.\d+)?|\w+(?:-\w+)*|\.\.\.|[&.,€£;%\$\"'?():-_]", text)
    # Dividere le parole che finiscono con couldn't aren't in -> could not    are not
    # Problema con will not = won't
    for word in words:
        if "n't" in word:
            if "won't" in word:
                verb = "will"
            elif "can't" in word:
                verb = "can"
            else:
                verb = word[0:-3]
                
            index = words.index(word)
            words.pop(index)
            if len(verb) != 0:
                words.insert(index, verb)
                words.insert(index+1, "not")
            else:
                # Caso in cui sia uno stacco n't
                words.insert(index, "not")
    return words
    
# Funzione per contare le sillabe 
def estraiSillabe(testi):
    sillabe = []
    

    
# Funzione che dato calcola la frequenza standardizzata delle parole nei testi, parametro per renderla case-sensitive oppure no
# frequenza assoluta x log ( numero documenti totale / numero documenti con quel termine) 
def getFrequencyIDF(wordsTexts, caseSensitive):
    frequencyWords = dict()
    nTexts = len(wordsTexts)
    index = 0
    for wordsText in wordsTexts:
        wordsReadText = []
        nWords = len(wordsText)
        #print(nWords)
        for word in wordsText:
            # Verifico il flag se il confronto è case sensitive oppure no
            if caseSensitive:
                wordLowerCase = word.lower()
            else:
                wordLowerCase = word
            if wordLowerCase in frequencyWords:
                frequencyWords[wordLowerCase][0][index] = frequencyWords[wordLowerCase][0][index] + 1
                if wordLowerCase not in wordsReadText:
                    wordsReadText.append(wordLowerCase)
                    frequencyWords[wordLowerCase][1] = frequencyWords[wordLowerCase][1] + 1
            else:
                #frequencyWords[wordLowerCase] = [1, 1]
                frequencyWords[wordLowerCase] = [ [], 1]
                # Inizializzo l'array per registrare le frequenze assolute della parola nei testi
                pedix = 0
                while pedix < nTexts:
                    frequencyWords[wordLowerCase][0].append(0)
                    pedix = pedix + 1
                # Ho trovato una parola nel testo nella posizione 'index'
                frequencyWords[wordLowerCase][0][index] = 1
                if wordLowerCase not in wordsReadText:
                    wordsReadText.append(wordLowerCase)
                
        # Divido le frequenze assolute del testo per il numero delle parole del testo per ottenere le frequenze relative
        for word in wordsReadText:
            #wordLowerCase = word.lower()
            #print(wordLowerCase)
            #print(frequencyWords[wordLowerCase][0][index])
            #print(nWords)
            frequencyWords[word][0][index] = frequencyWords[word][0][index] / nWords
        
        # Passaggio al testo successivo
        index = index + 1
    
    print(frequencyWords)
    
    frIdfWords = dict()
    for word in frequencyWords:
        idf = math.log10(nTexts/frequencyWords[word][1])
        frIdfWords[word] = []
        index = 0
        while index < len(frequencyWords[word][0]):
            frIdfWords[word].append(frequencyWords[word][0][index] * idf)
            index = index + 1
            
    return frIdfWords

# Funzione per calcolare  n-grams con parametro per scegliere il tipo di ngram (2-gram ecc) 
# Text => array di parole ottenuto con getWords()
# Number => n-gram che si vuole avere 2-bigram 3-trigram ecc
def getNGram(text, number):
    ngrams = []
    if number > 1:
        index = 0
        while index < len(text)-number+1:
            pedix = 0
            ngram = ""
            while pedix < number:  
                ngram = ngram + text[index+pedix].lower()
                if pedix+1 < number:
                    ngram = ngram + " "
                pedix = pedix + 1
            ngrams.append(ngram)
            index = index + 1
    return ngrams
 

# Funzione per allegare il tag null alla lista di parole data
def getWordsNullTag(words):
    nullTagWords = []
    for word in words:
        nullTagWords.append([word, "NULL"])
    return nullTagWords
 
# Funzione per ricavere i tag POS della frase data
# Ogni parola si ottiene il tag che può avere, successivamente in base alle regole 
'''def getPOSTags(sentence)
    sentenceTagged = []
    # Ottengo per ogni parola il tag che può avere
    for word in sentence:
        sentenceTagged.append([word, []])
        
    for wordTagged in sentenceTagged:
        # attraverso le regole cerca di ottenere un unico tag per ogni parola
        '''
# Funzioni per verificare l'appartenenza ad un gruppo di tag della parola
# I tag a gruppo chiuso, creo un array contenente le parole
# Per ogni parola verifico quali sono i tag che può avere 
# Successivamente in base ai tag che possono avere le parole si escludono quelli non possibili date le regole


'''
def getDictionaryNames()
    # Apro il file contenente i nomi e ignoro le prime 29 righe
    with open("names.txt", "r") as namesFile:
        
def getDictionaryVerbs()
    # Apro il file contenente i verbi e ignoro le prime 29 righe
    with open("verbs.txt", "r") as namesFile:
        
def getDictionaryAdverbs()
    # Apro il file contenente i avverbi e ignoro le prime 29 righe
    with open("adverbs.txt", "r") as namesFile:
    
def getDictionaryAdjectives()
    # Apro il file contenente gli aggettivi e ignoro le prime 29 righe 
    with open("adjectives.txt", "r") as namesFile:
    
# Funzioni per individuare i tag possibili della parola data
# Parametri: array di array di due elementi [parola, [tag1, tag2] ], indice della parola 

def isCC(sentence, index)
    # Lista chiusa
    conjunctions = ['for', 'and', 'not', 'but', 'or', 'yet', 'so']
    if sentence[index][0] in conjunctions:
        sentence[index][1] = 'CC'

def isCD(sentence, index)
    # Numeri basta un regex [0-9]+ anche first, second, third, fourth (-th), e one two three
    
def isDeterminer(sentence, index)
    # Lista chiusa
    determiners = ['the', 'a', 'an', 'this', 'that', 'these', 'those', 'all', 'both', 'much', 'many', 'some', 'any', 'enough', 'either', 'neither', 'each', 'every', 'other', 'another']
    if sentence[index][0] in determiners:
        sentence[index][1] = "DT"

def isExThere(sentence, index)
    # Se il there è all'inizio di there is o there are
    if sentence[index][0] == "there":
    
def isForeignWord()
    # TODO-
    pass
    
def isProposition(sentence, index)
    # Hanno un nome dopo

def isAdjective(sentence, index)
    # Lista degli aggettivi
    # Compartivi hanno more prima o finiscono per -er
    # Superlativi hanno most prima o finiscono per -est
    
def isListMarker(sentence, index)
    # TODO sarebbero 1. 2. lista numerata
    
def isModal(sentence, index)
    # Lista chiusa
    modals = ['can', 'could', 'must', 'have to', 'will', 'would', 'shall', 'might', 'shall']
    
def isNoun(sentence, index)
    # Lista dei nomi
    # finiscono con -s se sono al plurale --> NNS
    # Se ha lettere maiuscole ma non è all'inizio della frase potrebbe essere un nome proprio -> NNP 
    
def isPredeterminer(sentence, index)
    # Solitamente prima dell'articolo e possessive pronoun
    predeterminers = ['such', 'what', 'rather', 'quite', 'all']
    if sentence[index][0] in predeterminers:
        if 
def isPossessiveEnding(sentence, index)
    # Genitivo sassone ' o 's con nome prima
    if sentence[index][0] == "'" or ( sentence[index][0] == 's' and sentence[index-1][0] == "'" )
        
def isPersonalPronoun(sentence, index)
    # Lista chiusa
    personalPronouns = ['i', 'you', 'she', 'he', 'it', 'we', 'they', 'mine', 'ours', 'yours', 'thine', 'his', 'hers', 'its', 'theirs']
    
def isPossessivePronoun(sentence, index)
    # Lista chiusa
    possessivePronouns = ['my', 'your', 'her', 'his', 'its', 'our', 'their']
    
def isAdverb(sentence, index)
    # Lista di avverbi
    # finiscono per -ly
    # i comparativi hanno more prima o finiscono per -er
    # i superlativi hanno most prima o finiscono per -est

def isParticle(sentence, index)
    # Solitamente con un verbo 
    
def isSymbol(sentence, index)
    # Qualsiasi simbolo, basta una regex ,.?!-&
    
def isTo(sentence, index)
    # Semplicmente 'to'
    if sentence[index][0] == "to":
        sentence[index][1] = "TO"
    
def isInterjection(sentence, index)
    # Lista di interjection
    found = False
    interjections = ['aha', 'ahem', 'ahh', 'ahoy', 'alas', 'arg', 'aw', 'bam', 'bingo', 'blah', 'boo', 'bravo', 'brr', 'cheers', 'congratulations', 'dang', 'drat', 'darn', 'duh', 'eek', 'eh', 'encore', 'eureka','fiddlesticks', 'gadzooks', 'gee', 'gee whiz', 'golly', 'goodbye', 'goodness', 'good grief', 'gosh', 'ha-ha', 'hallelujah', 'hello', 'hey', 'hmm', 'holy buckets', 'holy cow', 'holy smokes', 'hot dog', 'huh', 'humph', 'hurray', 'oh','oh dear', 'oh my', 'oh well', 'ooops', 'ouch', 'ow', 'phew', 'phooey', 'pooh', 'pow', 'rats', 'shh', 'shoo', 'thanks', 'there', 'tut-tut', 'uh-huh', 'uh-oh', 'ugh', 'wahoo', 'well', 'whoa', 'whoops', 'wow', 'yeah', 'yes', 'yikes', 'yippee', 'yo', 'yuck']
    if sentence[index][0] in interjections:
        sentence[index][1] = "UH"
        found = True
    return found
    
def isVerb(sentence, index)
    verbs = getDictionaryVerbs()
    # VBD -> se finisce in -ed
    # VBG -> se finisce in -ing
    # VBN -> se finisce in -ed e ha ausiliare have/has/had prima
    # VBP -> se è presente non terza persona
    # VBZ -> se finisce con -s ,         se finisce con -s -z -x -ch -sh -> si aggiunge -es
    #        se finisce con y preceduta da una consonante cade la -y e si aggiunge -ies
    
def isWhDeterminer(sentence, index)
    # What e Which se non sono all'inizio della frase
    whDeterminers = ['what', 'which']
    if index != 0 and sentence[index][0] in whDeterminers:
        sentence[index][1] = "WDT"
        
def isWhPronoun(sentence, index)
    # what which who whoever all'inizio della frase
    whPronouns = ['what', 'which', 'who', 'whoever']
    if index == 0 and sentence[index][0] in whPronouns:
        sentence[index][1] = "WP"
    
def isWhPossession(sentence, index)
    # whom whose
    whPossession = ['whom', 'whose']
    if sentence[index][0] in whPossession:
        sentence[index][1] = "WP$"
        
def isWhAdverb(sentence, index)
    #when, where, why, how, whence, whereby, wherein, whereupon, how
    whAdverbs = ['when', 'where', 'why', 'how', 'whence', 'whereby', 'wherein', 'whereupon', 'how']
    if sentence[index][0] in whAdverbs:
        sentence[index][1] = "WRB"
# Funzione per ricavare la grammatica delle frasi'''