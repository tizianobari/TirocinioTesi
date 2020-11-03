import pickle

def getNameCategory(i):
    category = ""
    if i == 0:
        category = "title"
    if i == 1:
        category = "subtitle"
    if i == 2:
        category = "corpus"
    return category

def getSentences(words):
    sentences = []
    sentence = []
    for word in words:
        sentence.append(word)
        if word[1] == '.' or words.index(word)+1 == len(words):
            sentences.append(sentence)
            sentence = []
    return sentences

def getPcfg(words, terminals, nts):
    grammarPOS = dict()
    totalPOS = dict()
    for word in words:
        nonTerminal = str(nts.index(word[1]))
        terminal = str(terminals.index(word[0])+len(nts))
        rule = nonTerminal+" "+terminal+" -1"
        if rule not in grammarPOS:
            grammarPOS[rule] = 1
        else:
            grammarPOS[rule] = grammarPOS[rule] + 1
        
        if nonTerminal not in totalPOS:
            totalPOS[nonTerminal] = 1
        else:
            totalPOS[nonTerminal] = totalPOS[nonTerminal] + 1
    #print(grammarPOS)
    #print(totalPOS)
    pcfg = dict()
    for rule in grammarPOS:
        leftSideRule = rule.split(' ')[0]
        pcfg[rule] = grammarPOS[rule] / totalPOS[leftSideRule]
    
    return pcfg
    
#generalGrammar = pickle.load("../dataset/general.grammars", "rb"))
newsTagged = pickle.load(open("../dataset/politifact.csv.2.pos", "rb"))
nts = pickle.load(open("../dataset/politifact.csv.2.pos.nt", "rb"))

#file = open("politifact.pos.txt", "w")

#file.write(str(len(newsTagged))+"\n")

# Una notizia occupa 3 righe
for index in newsTagged:
    for j in range(len(newsTagged[index])):
        category = newsTagged[index][j]
        #file = open("politifact/"+index+"."+getNameCategory(j), "w")
        if type(category) == zip:
            words = list(category)
            terminalSentence = []
            grammarSentence = []
            sentences = getSentences(words)
            for indexSentence in range(len(sentences)):
                file = open("politifact/"+str(index)+"."+getNameCategory(j)+"."+str(indexSentence)+".txt", "w")
                # Ogni file una frase diversa
                file.write(str(len(sentences[indexSentence]))+"\n")
                # La frase da parsare
                for word in sentences[indexSentence]:
                    file.write(word[0])
                    if sentences[indexSentence].index(word)+1 != len(sentences[indexSentence]):
                        file.write("\t")
                file.write("\n")
                
                for word in sentences[indexSentence]:
                    if word[0] not in terminalSentence:
                        terminalSentence.append(word[0])
                # Scrittura dei terminali (numero terminali + lista terminali)
                file.write(str(len(terminalSentence))+"\n")
                for terminal in terminalSentence:
                    file.write(terminal)
                    if terminalSentence.index(terminal)+1 != len(terminalSentence):
                        file.write("\t")
                file.write("\n")
                
                pcfg = getPcfg(sentences[indexSentence], terminalSentence, nts)
                #Scrittura delle gramamtiche numero grammatiche + ( 1 per ogni riga )
                file.write(str(len(pcfg))+"\n")
                for rule in pcfg:
                    file.write(str(rule)+"\t"+str(pcfg[rule]))
                    if list(pcfg.keys()).index(rule)+1 != len(pcfg):
                        file.write("\n")
                
                terminalSentence = []
                grammarSentence = []
                
                file.close()
'''
for index in range(len(terminals)):
    fileTerminals.write(terminals[index])
    if index+1 != len(terminals):
        fileTerminals.write("\n")'''
        