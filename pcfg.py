import nltk
import buildPCFG
import pickle

def getGrammar(tree):
    grammars = dict()
    if type(tree) == nltk.tree.Tree:
        #print(tree.label())
        grammarString = splitTag(tree.label()) + " -> "
        index = 0
        while index < len(tree):
            child = tree[index]
            if type(child) == str:
                grammarString = grammarString + splitTag(child)
                #print("Foglia a")
            else:
                grammarString = grammarString + splitTag(child.label())
                addDict(grammars, getGrammar(child))
            if index+1 < len(tree):
                grammarString = grammarString + " "
            index = index + 1
        # Metto la grammatica nel dizionario
        if grammarString not in grammars:
            if len(tree) == 1 and type(tree[0]) == str:
                # Indico che è una foglia ( secondo elemento = 1 )
                grammars[grammarString] = [1, 1]
            else:
                grammars[grammarString] = [1, 0]
        else:
            grammars[grammarString][0] = grammars[grammarString][0] + 1
        #print(grammars[grammarString])
    return grammars
    
def addDict(dict, dictToAdd):
    for key in dictToAdd:
        if key not in dict:
            dict[key] = dictToAdd[key]
            #dict[key] = [dictToAdd[key][0], dictToAdd[key][1]]
        else:
            dict[key][0] = dict[key][0] + dictToAdd[key][0]
    
def splitTag(tag):
    if tag == "-NONE-":
        t = tag
    else:
        t = tag.split("-")[0].split("=")[0]
    return t
    
#Funzione per ottenere la grammatica con le probabilità
def getProbabiltyGrammar(bgrammars, totalGrammars):
    probGrammars = dict()
    #print(bgrammars)
    for rule in bgrammars:
        leftSideRule = rule.split('->')[0].strip()
        probGrammars[rule] = bgrammars[rule][0] / totalGrammars[leftSideRule]
        '''if probGrammars[rule] == 1.0:
            print(rule)
            #print("\t"+str(bgrammars[rule][0])+"/"+str(totalGrammars[leftSideRule]))'''
    return probGrammars
 
# Funzione che somma tutte le probabilità
def checkProbabilityGrammar(grammars):
    checkPGrammars = dict()
    for key in grammars:
        # Ottengo la parte sinistra della regola
        rule = key.split('->')[0].strip()
        if rule not in checkPGrammars:
            checkPGrammars[rule] = grammars[key]
        else:
            checkPGrammars[rule] = checkPGrammars[rule] + grammars[key]
    return checkPGrammars
    
if __name__ == "__main__":
    sentencesParsed = nltk.corpus.treebank.parsed_sents()
    grammars = dict()

    for sentenceParsed in sentencesParsed:
        addDict(grammars, getGrammar(sentenceParsed))
        
    print(len(grammars))
        
    # Pulisco la grammatica levando le regole con <= 5 occorrenze e le foglie
    clearGrammars = dict()
    for key in grammars:
        if grammars[key][0] > 0 and grammars[key][1] == 0:
            clearGrammars[key] = grammars[key]      

       

     
    print("Numero grammatiche con occorrenze > 5")
    print(len(clearGrammars))
     
    # Rimuovo le regole con simboli non terminali a destra che non hanno una regola definita
    '''checked = False
    nonTerminalSymbols = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NN', 'NNS', 'NNP', 'NNPS', 'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB', '#', '"', '""', ".", ",", "``" ]
    while not checked:
        index = 0
        checked = True
        while index < len(clearGrammars):
            key = list(clearGrammars.keys())[index]
            ruleSplitted = buildPCFG.getSidesRule(key)
            rightSide = ruleSplitted[1]
            ruleFound = 0
            i = 0
            #print("Studiando la regola "+key)
            #print("\t"+str(rightSide))
            while i < len(rightSide):
                j = 0
                found = False
                while j < len(clearGrammars) and not found:
                    ls = list(clearGrammars.keys())[j][0]
                    if rightSide[i] == ls or rightSide[i] in nonTerminalSymbols:
                        #print("\tTrovata corrispondenza per indice "+str(i)+"! "+ rightSide[i])
                        found = True
                        ruleFound = ruleFound + 1
                    j = j + 1
                i = i + 1
            # Se non ho trovato la regola per entrambi i simboli non terminali cancello la regola ed esco dal for 
            if ruleFound < len(rightSide):
                print(key+" i simboli non terminali a destra non hanno una regola")
                clearGrammars.pop(key)
                checked = False
                break
            index = index + 1
    '''        
    print("Dopo ripulimento")
    print(len(clearGrammars))
     
    # Rendo le grammatiche binarie
    binaryGrammars = dict()
    for key in clearGrammars:
        ruleSplitted = buildPCFG.getSidesRule(key)
        leftSide = ruleSplitted[0]
        rightSide = ruleSplitted[1]
        # Verifico che non ci sia il tag "-NONE-" altrimenti non lo considero
        if "-NONE-" not in rightSide:
            if len(rightSide) > 2:
                rule = clearGrammars[key]
                createdNT = []
                while len(rightSide) > 2:
                    # Iterazione per fondere due simboli non terminali non generati
                    index = 0
                    while index < len(rightSide)-1:
                        #if rightSide[index] not in createdNT and rightSide[index+1] not in createdNT:
                        r2 = rightSide.pop(index+1)
                        r1 = rightSide.pop(index)
                        tagCreated = "X"+r1+r2
                        createdNT.append(tagCreated)
                        createdRule = tagCreated + " -> "+r1+" "+r2
                        if createdRule not in binaryGrammars:
                            binaryGrammars[createdRule] = [1, 0]
                        rightSide.insert(index, tagCreated)
                        index = index + 1
                        #print("Incrementato indice a : "+str(index))
                        #print("Lunghezza pari a "+str(len(rightSide)))
                # Alla fine dell'iterazione avrò la regola in forma binaria
                binaryRule = leftSide+" -> "+rightSide[0]+" "+rightSide[1]
                binaryGrammars[binaryRule] = [rule[0], 0]
                #print(binaryRule + "--" +str(binaryGrammars[binaryRule]))
            else:
                binaryGrammars[key] = clearGrammars[key]
        else:
            print("Regola con -NONE-"+str(key))
    print(binaryGrammars)
            
    sumBinary = 0
    for i in binaryGrammars:
        sumBinary = sumBinary + binaryGrammars[i][0]
    print("Somma totale di binaryGrammars: "+str(sumBinary))
            
    # Ottengo la somma delle grammatiche
    totalGrammars = dict()
    for key in binaryGrammars:
        # Ottengo la parte sinistra della regola
        rule = key.split('->')[0].strip()
        if rule not in totalGrammars:
            totalGrammars[rule] = binaryGrammars[key][0]
        else:
            totalGrammars[rule] = totalGrammars[rule] + binaryGrammars[key][0]

    print(binaryGrammars)        
            

    sumTotal = 0
    for i in totalGrammars:
        sumTotal = sumTotal + totalGrammars[i]
    print("Somma totale di totalGrammars: "+str(sumTotal))
            

    print(len(totalGrammars))
        
    # Totale grammatiche pulite
            
    #print(totalGrammars)        
            
    probabilityGrammars = getProbabiltyGrammar(binaryGrammars, totalGrammars)

    '''listGrammars = []
    for grammar in grammars:
            listGrammars.append(grammar)'''

    #print(listGrammars)
    
    '''print("Inducing pcfg grammars using nltk library!")
    print(listGrammars[3])
    pcfg = nltk.PCFG.fromstring(listGrammars)
    print(pcfg)'''
    
    # Ottengo i simboli non terminali della grammatica
    nonTerminals = []
    for key in probabilityGrammars:
        ruleSplitted = buildPCFG.getSidesRule(key)
        leftSide = ruleSplitted[0]
        rightSide = ruleSplitted[1]
        if leftSide not in nonTerminals:
            nonTerminals.append(leftSide)
        for nt in rightSide:
            if nt not in nonTerminals:
                nonTerminals.append(nt)
    print(str(len(nonTerminals)))
    
    
    checkPGrammars = dict()
    for key in probabilityGrammars:
        # Ottengo la parte sinistra della regola
        rule = key.split('->')[0].strip()
        if rule not in checkPGrammars:
            checkPGrammars[rule] = probabilityGrammars[key]
        else:
            checkPGrammars[rule] = checkPGrammars[rule] + probabilityGrammars[key]
            
    #print(grammars)
    print(checkPGrammars)

    file = open("grammatiche-probabilita.txt", "w")
    ordinato = sorted(probabilityGrammars.items(), key=lambda x: x[1])
    for item in ordinato:
        file.write(item[0]+"\t"+ str(item[1])+"\n")
    file.close()
    
    # Salvo in un file la grammatica generale
    pickle.dump(probabilityGrammars, open("dataset/general.grammars", "wb"))
    
    # Unione delle grammatiche con i POS
    #posPolitifact = pickle.load(open("dataset/gossipcop.csv.2.pos","rb"))
    filenames = ['dataset/gossipcop.csv.2.pos', 'dataset/politifact.csv.2.pos']
    #print(tuple(posPolitifact[2][0]))
    # Ogni riga corrisponde ad una notizia, ogni elemento corrisponde a titolo, sottotitolo e corpus
    # Ogni parola è la coppia ('parola', 'tag')
    for filename in filenames:
        posDataset = pickle.load(open(filename,"rb"))
        grammarPOS = dict()
        totalPOS = dict()
        for row in posDataset.values():
            for text in row:
                tupleText = tuple(text)
                if tupleText != ():
                    for element in tupleText:
                        rule = element[1]+" -> "+element[0]
                        if rule not in grammarPOS:
                            grammarPOS[rule] = [1, 1]
                        else:
                            grammarPOS[rule][0] = grammarPOS[rule][0] + 1
                        
                        if element[1] not in totalPOS:
                            totalPOS[element[1]] = 1
                        else:
                            totalPOS[element[1]] = totalPOS[element[1]] + 1
                
        print(grammarPOS)
        print(totalPOS)
    
        # Toglo le regole con tag -NONE- se ce ne sono
        '''for key in grammarPOS:
            rule = buildPCFG.getSidesRule(key)
            if rule[0] == "-NONE-":
                print(key)'''
        
        probPOS = getProbabiltyGrammar(grammarPOS, totalPOS)
        print("Somma probabilità pos da sole")
        print(checkProbabilityGrammar(probPOS))
        
        # Unisco la grammatica delle regole di scrittura con i tag pos del dataset interessato
        addDict(probPOS, probabilityGrammars)
        print("Somma probabilità grammatiche del dataset")
        print(checkProbabilityGrammar(probPOS))
        
        # Aggiungo le grammatiche dei simboli base
        basePunctGrammars = ['# -> #', '$ -> $', '"" -> ""', "`` -> ``"]
        for baseGrammar in basePunctGrammars:
            if baseGrammar not in probPOS:
                probPOS[baseGrammar] = 1.0
        
        # Salvo la grammatica totale del dataset in un file
        pickle.dump(probPOS, open(filename+".grammar", "wb"))
        
        nonTerminalsDataset = []
        nonTerminalsDataset = nonTerminalsDataset + nonTerminals
        # Ottengo i simboli non terminali dalla grammatica pos (possibili duplicati)
        for key in grammarPOS:
            ruleSplitted = buildPCFG.getSidesRule(key)
            leftSide = ruleSplitted[0]
            if leftSide not in nonTerminalsDataset:
                nonTerminalsDataset.append(leftSide)
        
        print(nonTerminalsDataset)
        pickle.dump(nonTerminalsDataset, open(filename+".nt", "wb"))
        
        '''
        # Divido le grammatiche con le probabilità in frasi e le salvo in file differenti
        # molto pesante
        posDataset = pickle.load(open(filename,"rb"))
        newsListSentences = []
        # Iterazione per analizzare ogni notizia
        for news in posDataset.values():
            newsCategories = []
            print("Analizzo la notizia del dataset: "+filename)
            # Iterazione per analizzare ogni categoria della notizia
            #print(news)
            for category in news:
                catSentences = []
                print("\tAnalizzo la categoria")
                if type(category) == zip:
                    wordsCategory = list(category)
                    catSentence = dict()
                    totalSentence = dict()
                    # Iterazione per analizzare le parole della categoria della notizia
                    for index in range(len(wordsCategory)):
                        word = wordsCategory[index]
                        rule = word[1] + " -> " + word[0]
                        if rule not in catSentence:
                            catSentence[rule] = [1, 1]
                        else:
                            catSentence[rule][0] = catSentence[rule][0] + 1
                        
                        if word[1] not in totalSentence:
                            totalSentence[word[1]] = 1
                        else:
                            totalSentence[word[1]] = totalSentence[word[1]] + 1
            
                        # Se la parola che ho letto è un simbolo di punteggiatura tra . ! ? oppure è l'ultima parola -> 
                        # la frase è finita, calcolo la grammatica
                        if word[1] in ['.', '!', '?'] or index+1 == len(wordsCategory):
                            print("\t\t frase analizzata!")
                            probCat = getProbabiltyGrammar(catSentence, totalSentence)
                            # Aggiungo la probabilità della grammatica generata dalla treebank
                            addDict(probCat, probabilityGrammars)
                            catSentences.append(probCat)
                            # Passo alla frase successiva
                            catSentence = dict()
                            totalSentence = dict()
                newsCategories.append(catSentences)
            newsListSentences.append(newsCategories)
        pickle.dump(newsListSentences, open(filename+".sentences.grammar", "wb"))'''
        