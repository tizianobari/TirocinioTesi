# N simboli non terminali: NP, PP, IN .. ottenute tramite le grammatiche dal corpus treebank
# E simboli terminali: pos tags 
# R regole non terminali -> non terminali o terminali
# S start symbol

# Ogni gruppo lo salvo in un file

# Verifico la sintassi delle regole scritte
# Le regole nel file sono strutturate con regola \t probabilità 
# La regola è strutturata come NonTerminale -> NonTerminale ... NonTerminale oppure NonTerminale -> Terminale
import math

def getSidesRule(rule):
    d = []
    splitted = rule.split("->")
    leftSide = splitted[0].strip()
    rightSide = splitted[1].strip().split(" ")
    d = [leftSide ,rightSide]
    return d

def buildTreeParse(back, words, start, end, symbol):
    tree = []  
    #print("print tree:")
    #print(back[start][end])
    print(symbol)
    if back[start][end][symbol] != "":
        #print(symbol)
        split = back[start][end][symbol][0]
        i = 1
        if len(back[start][end][symbol]) == 3:
            child1 = back[start][end][symbol][1]
            child2 = back[start][end][symbol][2]
            #print(child1)
            #printTreeParse(back, words, start, split, child1)
            #print(child2)
            #printTreeParse(back, words, split+1, end, child2)
            tree = [symbol, printTreeParse(back, words, start, split, child1), printTreeParse(back, words, split+1, end, child2)]
        else:
            child1 = back[start][end][symbol][1]
            printTreeParse(back, words, start, end, child1)
    else:
        print(words[start])
        tree = [symbol, words[start]]
    return tree
    
 

def cykParsing(words, grammar, nonTerminals, terminals):
    nWords = len(words)
    nGrammars = len(grammar)
    table = []
    back = []
    # Creazione matrici 3d
    for i in range(len(words)):
        table.append([])
        back.append([])
        for j in range(len(words)):
            table[i].append(dict())
            back[i].append(dict())
            for nonTerminal in nonTerminals:
                table[i][j][nonTerminal] = 0.0
                back[i][j][nonTerminal] = ""
                
    # Inizializzazione matrice con probabilità delle regole X -> xi delle parole
    # Da sistemare! Controllo delle parole e delle grammatiche !
    for i in range(len(words)):
        for rule in grammar:
            ruleSplitted = getSidesRule(rule[0])
            leftSide = ruleSplitted[0]
            rightSide = ruleSplitted[1]
            if len(rightSide) == 1 and rightSide[0] == words[i]:
                print("Probabilità parola: "+words[i]+" = "+str(rule[1]))
                table[i][i][leftSide] = rule[1]
                print("\tSettato nella tabella con indice "+str(i)+"-"+str(i)+" e regola: "+leftSide)
            else:
                if leftSide not in table[i][i]:
                    table[i][i][leftSide] = 0.0
        print("\tStampa della riga "+str(i)+": "+str(table[i][i]))
    
    
    # Algoritmo per calcolare le probabilità degli alberi
    length = 1
    while length < nWords:
        print("Lunghezza intervallo = "+str(length))
        i = 0
        while i < nWords-length:
            j = i + length
            split = i
            # è j o j-1???
            while split < j:
                print("\tStudio la regola binaria con sottostringhe pari a : "+str(i)+"-"+str(split)+" e "+str(split+1)+"-"+str(j))
                # Indice di split della frase
                for rule in grammar:
                    #print("\t\t Regola = "+rule[0])
                    ruleSplitted = getSidesRule(rule[0])
                    rightSide = ruleSplitted[1]
                    leftSide = ruleSplitted[0]
                    # Verifico se la regola è binaria o unaria
                    if len(rightSide) == 2:
                        #print("I = "+str(i))
                        #print("Length = "+str(length))
                        #print("J = "+str(j))
                        #logaritmo sommo invece che moltiplico
                        #print("\t\tVerifica della regola "+rule[0]+" con probabilita totale: "+str(rule[1] * table[i][split][rightSide[0]] * table[split+1][j][rightSide[1]])+ " trovata da regola con p = "+str(rule[1])+" * "+str(table[i][split][rightSide[0]])+" * "+str(table[split+1][j][rightSide[1]]))
                        #print("\t\t\t Regola sinistra: "+leftSide)
                        #print("\t\t\t Regola destra 1: "+rightSide[0])
                        #print("\t\t\t Regola destra 2: "+rightSide[1])
                        #print("\t\t\t\t "+str(table[i][split]))
                        #print("\t\t\t\t "+str(table[split+1][j]))
                        #print(table[i][split][rightSide[0]] != 0.0)
                        #print(table[split+1][j][rightSide[1]] != 0.0)
                        #print(table[i][split][rightSide[0]] != 0.0 and table[split+1][j][rightSide[1]] != 0.0)
                        
                        if table[i][split][rightSide[0]] != 0.0 and table[split+1][j][rightSide[1]] != 0.0:
                            #probSplitting = math.log10(rule[1]) + math.log10(table[i][split][rightSide[0]]) + math.log10(table[split+1][j][rightSide[1]])
                            probSplitting = rule[1] * table[i][split][rightSide[0]] * table[split+1][j][rightSide[1]]
                            #print("Verifica della regola "+rule[0]+": per partizione "+str(i)+"-"+str(split)+" e "+str(split+1)+"-"+str(j) + " con probabilita totale: "+str(probSplitting)+ "trovata da regola con p = "+str(rule[1])+" * "+str(table[i][split][rightSide[0]])+" * "+str(table[split+1][j][rightSide[1]]))
                            if probSplitting > table[i][j][leftSide]:
                                print("\t\t\t OK! della regola "+rule[0]+": per partizione "+str(i)+"-"+str(split)+" e "+str(split+1)+"-"+str(j) + " con probabilita totale: "+str(probSplitting)+ " trovata da regola con p = "+str(rule[1])+" * "+str(table[i][split][rightSide[0]])+" * "+str(table[split+1][j][rightSide[1]]))
                                table[i][j][leftSide] = probSplitting
                                back[i][j][leftSide] = [split, rightSide[0], rightSide[1]]
                    elif len(rightSide) == 1 and rightSide[0] in nonTerminals:
                        ruleSplitted = getSidesRule(rule[0])
                        rightSide = ruleSplitted[1]
                        leftSide = ruleSplitted[0]
                        #print("\tRegola unaria: "+rule[0])
                        if table[i][split][rightSide[0]] != 0.0:
                            probSplitting = rule[1] * table[i][split][rightSide[0]]
                            if probSplitting > table[i][split][leftSide]:
                                print("\t\t 1OK! della regola "+rule[0]+": per partizione unaria "+str(i)+"-"+str(split)+" con probabilita: "+str(probSplitting))
                                table[i][split][leftSide] = probSplitting
                                back[i][split][leftSide] = [split, rightSide[0]]
                split = split + 1
            
            i = i + 1
        length = length + 1
    #print(table)
    #print(back)
    print(table[0][nWords-1]["S"])
    for i in range(len(back)):
        for j in range(len(back)):
            for n in back[i][j]:
                if back[i][j][n] != "":
                    print("Tupla trovata in : "+str(i)+"-"+str(j)+" "+str(n)+" -> "+str(back[i][j][n]))
    
    if back[0][nWords-1]['S'] != 0.0:
        print(buildTreeParse(back, words, 0, nWords-1, 'S'))
    #print(back[0][nWords-1]['S'])

        

if __name__ == "__main__":
    
    # Esempio
    words = ["I" ,"saw", "John", "with", "my", "telescope"]
    # [0] -> regola
    # [1] -> probabilità
    grammar = [
        ["S -> NP VP", 1.0],
        ["NP -> Det N", 0.5],
        ["NP -> NP PP", 0.25],
        ["NP -> John", 0.1],
        ["NP -> I", 0.15],
        ["Det -> the", 0.8],
        ["Det -> my", 0.2],
        ["N -> man", 0.5],
        ["N -> telescope", 0.5],
        ["VP -> VP PP", 0.1],
        ["VP -> V NP", 0.7],
        ["VP -> V", 0.2],
        ["V -> ate", 0.35],
        ["V -> saw", 0.65],
        ["PP -> P NP", 1.0],
        ["P -> with", 0.61],
        ["P -> under", 0.39]
    ]
    nonTerminal = ["S", "NP", "VP", "PP", "Det", "V", "P", "N"]
    terminal = ["John", "I", "the", "my", "man", "telescope", "ate", "saw", "with", "under"]
    #cykParsing(words, grammar)
    cykParsing(words, grammar, nonTerminal, terminal)

    
