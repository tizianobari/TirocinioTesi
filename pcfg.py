import nltk
import buildPCFG

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
        else:
            dict[key][0] = dict[key][0] + dictToAdd[key][0]
    
def splitTag(tag):
    if tag == "-NONE-":
        t = tag
    else:
        t = tag.split("-")[0]
    return t
    
def getProbabiltyGrammar(bgrammars, totalGrammars):
    probGrammars = dict()
    print(bgrammars)
    for rule in bgrammars:
        leftSideRule = rule.split('->')[0].strip()
        probGrammars[rule] = bgrammars[rule][0] / totalGrammars[leftSideRule]
        if probGrammars[rule] == 1.0:
            print(rule)
            print("\t"+str(bgrammars[rule][0])+"/"+str(totalGrammars[leftSideRule]))
    return probGrammars
        
    
sentencesParsed = nltk.corpus.treebank.parsed_sents()
grammars = dict()

for sentenceParsed in sentencesParsed:
    addDict(grammars, getGrammar(sentenceParsed))
    
print(len(grammars))
    
# Pulisco la grammatica levando le regole con <= 5 occorrenze e le foglie
clearGrammars = dict()
for key in grammars:
    if grammars[key][0] > 5 and grammars[key][1] == 0:
        clearGrammars[key] = grammars[key]
        
print(len(clearGrammars))
    
    
# Rendo le grammatiche binarie
binaryGrammars = dict()
for key in clearGrammars:
    ruleSplitted = buildPCFG.getSidesRule(key)
    leftSide = ruleSplitted[0]
    rightSide = ruleSplitted[1]
    if len(rightSide) > 2:
        # Rimuovo la regola
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

listGrammars = []
for grammar in grammars:
        listGrammars.append(grammar)

#print(listGrammars)

'''print("Inducing pcfg grammars using nltk library!")
print(listGrammars[3])
pcfg = nltk.PCFG.fromstring(listGrammars)
print(pcfg)'''

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
    file.write(item[0]+" : "+ str(item[1])+"\n")
file.close()