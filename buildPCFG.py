# N simboli non terminali: NP, PP, IN .. ottenute tramite le grammatiche dal corpus treebank
# E simboli terminali: pos tags 
# R regole non terminali -> non terminali o terminali
# S start symbol

# Ogni gruppo lo salvo in un file

# Verifico la sintassi delle regole scritte
# Le regole nel file sono strutturate con regola \t probabilità 
# La regola è strutturata come NonTerminale -> NonTerminale ... NonTerminale oppure NonTerminale -> Terminale
import math
import pickle
import functions
import pcfg

def getSidesRule(rule):
    d = []
    #print(rule)
    splitted = rule.split("->")
    # print(splitted)
    leftSide = splitted[0].strip()
    #print(leftSide)
    rightSide = splitted[1].strip().split(" ")
    #print(rightSide)
    d = [leftSide ,rightSide]
    return d

    
#buildTreeParse(back, words, 0, nWords-1, 'S') -- inizio
def buildTreeParse(back, words, start, end, symbol):
    tree = []  
    #print("print tree:")
    #print(back[start][end])
    #print(symbol)
    # Verifica che non sia un simbolo terminale / parola
    if back[start][end][symbol] != "":
        #print(symbol)
        split = back[start][end][symbol][0]
        i = 1
        # Verifica che sia una grammatica binaria oppure unaria
        if len(back[start][end][symbol]) == 3:
            child1 = back[start][end][symbol][1]
            child2 = back[start][end][symbol][2]
            #print(child1)
            #printTreeParse(back, words, start, split, child1)
            #print(child2)
            #printTreeParse(back, words, split+1, end, child2)
            #if symbol[0] != 'X':
            tree = [symbol, buildTreeParse(back, words, start, split, child1), buildTreeParse(back, words, split+1, end, child2)]
            #else:
                #tree = [buildTreeParse(back, words, start, split, child1), buildTreeParse(back, words, split+1, end, child2)]
        else:
            child1 = back[start][end][symbol][1]
            #print(child1)
            tree = [symbol, buildTreeParse(back, words, start, end, child1)]
    else:
        #print(words[start])
        tree = [symbol, words[start]]
    return tree

# Funzione per fixare il problema della sostituzione delle grammatiche ausiliari XNT1NT2
def fixTreeParse(tree):
    index = 1
    while index < len(tree):
        fixTreeParse(tree[index])
        index = index +1
    # Levo il nodo con il simbolo non terminale ausiliario e lo sostituisco con il suo sottoalbero    
    index = 1
    while index < len(tree):
        if tree[index][0][0] == 'X':
            # è una grammatica ausiliara, devo rendere il suo sottoalbero figli del nodo corrente
            aux = tree.pop(index)
            pedix = len(aux)-1
            while pedix >= 1:
                tree.insert(index, aux[pedix])
                pedix = pedix - 1
        else:
            index = index + 1
    return tree
    
# ['S', ['VP', ['V', 'saw'], ['NP', ['NP', 'John'], ['PP', ['P', 'with'], ['NP', ['Det', 'my'], ['N', 'telescope']]]]], ['.', '.']]
# ['S', ['VP^S', ['V^VP', 'saw'], ['NP^S', ['NP^NP', 'John'], ['PP^NP', ['P^PP', 'with'], ['NP^PP', ['Det^NP', 'my'], ['N^NP', 'telescope]]]]], ['.^S', '.']]
# Unlexicalized = senza nodi terminali
def getLexicalizedProductions(tree):
    productions = []
    if type(tree) == list:
        leftSide = tree[0]
        production = leftSide + " -> "
        index = 1
        while index < len(tree):
            if type(tree[index]) == list:
                child = tree[index][0]
            else:
                child = tree[index]
            production = production + child
            if index+1 != len(tree):
                production = production + " "
            index = index + 1
        productions.append(production)
        
        # Chiamata della funzione per i sottoalberi
        index = 1
        while index < len(tree):
            productions = productions + getLexicalizedProduction(tree[index])
            index = index + 1
        
    return productions
    
# Accorpare le funzioni?
def getUnlexicalizedProductions(tree):
    productions = []
    if type(tree) == list and not (len(tree) == 2 and type(tree[1]) == str):
        leftSide = tree[0]
        production = leftSide + " -> "
        index = 1
        while index < len(tree):
            child = tree[index][0]
            production = production + child
            if index+1 != len(tree):
                production = production + " "
            index = index + 1
        productions.append(production)
        
        # Chiamata della funzione per i sottoalberi
        index = 1
        while index < len(tree):
            productions = productions + getUnlexicalizedProductions(tree[index])
            index = index + 1
    return productions
    
def getLexicalizedProductionsGP(tree, gp):
    productions = []
    if type(tree) == list:
        leftSide = tree[0]
        production = leftSide + '^'
        if gp == '':
            production = production + "ROOT"
        else:
            production = production + gp
        production = production + " -> "
        
        index = 1
        while index < len(tree):
            if type(tree[index]) == list:
                child = tree[index][0]
            else:
                child = tree[index]
            production = production + child
            if index+1 != len(tree):
                production = production + " "
            index = index + 1
        productions.append(production)
        # Chiamata della funzione per i sottoalberi
        index = 1
        while index < len(tree):
            productions = productions + getLexicalizedProductionsGP(tree[index], leftSide)
            index = index + 1
    return productions
    
def getUnlexicalizedProductionsGP(tree, gp):
    productions = []
    if type(tree) == list and not (len(tree) == 2 and type(tree[1]) == str):
        leftSide = tree[0]
        production = leftSide + '^'
        if gp == '':
            production = production + "ROOT"
        else:
            production = production + gp
        production = production + " -> "
        index = 1
        while index < len(tree):
            child = tree[index][0]
            production = production + child
            if index+1 != len(tree):
                production = production + " "
            index = index + 1
        productions.append(production)
        
        # Chiamata della funzione per i sottoalberi
        index = 1
        while index < len(tree):
            productions = productions + getUnlexicalizedProductionsGP(tree[index], leftSide)
            index = index + 1
    return productions

def cykParsing(words, grammar, nonTerminals, terminals):
    nWords = len(words)
    nGrammars = len(grammar)
    table = []
    back = []
    # Creazione matrici 3d
    print("cykparsing - creazione matrici")
    for i in range(len(words)):
        table.append([])
        back.append([])
        for j in range(len(words)):
            table[i].append(dict())
            back[i].append(dict())
            for nonTerminal in nonTerminals:
                table[i][j][nonTerminal] = 0.0
                back[i][j][nonTerminal] = ""
    print("cykparsing - matrici create")            
    # Inizializzazione matrice con probabilità delle regole X -> xi delle parole
    # Da sistemare! Controllo delle parole e delle grammatiche !
    print("inizializzazione matrici con probabilità delle parole")
    for i in range(len(words)):
        for rule in grammar:
            #print("\t "+str(i)+": studio regola "+rule[0])
            ruleSplitted = getSidesRule(rule[0])
            leftSide = ruleSplitted[0]
            rightSide = ruleSplitted[1]
            if len(rightSide) == 1 and rightSide[0] == words[i]:
                #print("Probabilità parola: "+words[i]+" = "+str(rule[1]))
                table[i][i][leftSide] = rule[1]
                #print("\tSettato nella tabella con indice "+str(i)+"-"+str(i)+" e regola: "+leftSide)
            else:
                if leftSide not in table[i][i]:
                    table[i][i][leftSide] = 0.0
        #print("\tStampa della riga "+str(i)+": "+str(table[i][i]))
    
    
    # Algoritmo per calcolare le probabilità degli alberi
    length = 1
    while length < nWords:
        #print("Lunghezza intervallo = "+str(length))
        i = 0
        while i < nWords-length:
            j = i + length
            split = i
            # è j o j-1???
            while split < j:
                #print("\tStudio la regola binaria con sottostringhe pari a : "+str(i)+"-"+str(split)+" e "+str(split+1)+"-"+str(j))
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
                                #print("\t\t\t OK! della regola "+rule[0]+": per partizione "+str(i)+"-"+str(split)+" e "+str(split+1)+"-"+str(j) + " con probabilita totale: "+str(probSplitting)+ " trovata da regola con p = "+str(rule[1])+" * "+str(table[i][split][rightSide[0]])+" * "+str(table[split+1][j][rightSide[1]]))
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
                                #print("\t\t 1OK! della regola "+rule[0]+": per partizione unaria "+str(i)+"-"+str(split)+" con probabilita: "+str(probSplitting))
                                table[i][split][leftSide] = probSplitting
                                back[i][split][leftSide] = [split, rightSide[0]]
                split = split + 1
            
            i = i + 1
        length = length + 1
    #print(table)
    #print(back)
    print(table[0][nWords-1]["S"])
    '''for i in range(len(back)):
        for j in range(len(back)):
            for n in back[i][j]:
                if back[i][j][n] != "":
                    print("Tupla trovata in : "+str(i)+"-"+str(j)+" "+str(n)+" -> "+str(back[i][j][n]))'''

    tree = ""
    if table[0][nWords-1]['S'] != 0.0:
        tree = buildTreeParse(back, words, 0, nWords-1, 'S')
    #print(back[0][nWords-1]['S'])
    else:
        print("Non è stato possibile fare calcolare la grammatica")
        #print(words)
    #print(tree)
    return tree

# Funzione provvisoria per rendere il dizionario delle grammatiche in una lista
# per la funzione del parsing
def dictToList(diz):
    list = []
    for grammar in diz:
        list.append([grammar, diz[grammar]])
    return list
    
if __name__ == "__main__":
    example = False
    if example:
        # Esempio
        words = ["I" ,"saw", "John", "with", "my", "telescope", "."]
        # [0] -> regola
        # [1] -> probabilità
        grammar = [
            ["XNPVP -> NP VP", 1.0],
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
            ["P -> under", 0.39],
            ["S -> XNPVP .", 1.0],
            [". -> .", 1.0]
        ]
        nonTerminal = ["S", "NP", "VP", "PP", "Det", "V", "P", "N", ".", "XNPVP"]
        terminal = ["John", "I", "the", "my", "man", "telescope", "ate", "saw", "with", "under", "."]
        cykParsing(words, grammar, nonTerminal, terminal)
    else:
        # Carico le grammatiche
        filenames = ['dataset/politifact', 'dataset/gossipcop']
        #filenames = ['gossipcop.csv.2.pos.grammar', 'politifact.csv.2.pos.grammar']
        for filename in filenames:
            grammarsGeneral = pickle.load(open("dataset/general.grammars", "rb"))
            #newsTagged: ogni riga ha 3 elementi riguardanti il titolo, sottotitolo e articolo
            newsTagged = pickle.load(open(filename+".csv.2.pos", "rb"))
            nonTerminals = pickle.load(open(filename+".csv.2.pos.nt", "rb"))
            terminal = []
                        
            # Per ogni articolo ricavo la grammatica
            print("Ricavo la grammatica per ogni articolo")
            newsParsed = []
            #print(newsTagged)
            for news in newsTagged.values():
                print(filename + "notizia numero " +str(news))
                n = []
                for category in news:
                    c = []
                    if type(category) == zip:
                        wordsCategory = list(category)
                        #print(wordsCategory)
                        if len(wordsCategory) > 0:
                            #print("La categoria ha delle parole")
                            sentences = []
                            sentence = []
                            # Ottengo le frasi con i pos
                            for index in range(len(wordsCategory)):
                                word = wordsCategory[index]
                                sentence.append(word)
                                if word[1] in ['.','!','?'] or index+1 == len(wordsCategory):
                                    sentences.append(sentence)
                                    sentence = []
                            
                            for sentence in sentences:
                                #print(sentence)
                                # Ottengo la grammatica dei simboli non terminali -> simboli terminali della frase
                                grammarPOS = dict()
                                totalPOS = dict()
                                for word in sentence:
                                    rule = word[1]+" -> "+word[0]
                                    if rule not in grammarPOS:
                                        grammarPOS[rule] = [1, 1]
                                    else:
                                        grammarPOS[rule][0] = grammarPOS[rule][0] + 1
                                    
                                    if word[1] not in totalPOS:
                                        totalPOS[word[1]] = 1
                                    else:
                                        totalPOS[word[1]] = totalPOS[word[1]] + 1
                                        
                                probPOS = pcfg.getProbabiltyGrammar(grammarPOS, totalPOS)
                                # Unisco la grammatica delle regole di scrittura con i tag pos della frase interessata
                                pcfg.addDict(probPOS, grammarsGeneral)
                                
                                #print(probPOS)
                                
                                listProbPOS = dictToList(probPOS)
                                
                                # Ottengo l'array delle parole senza pos tag
                                wordsSentence = []
                                for words in sentence:
                                    wordsSentence.append(words[0])
                                
                                print(sentence)
                                #print(str(len(wordsSentence)))
                                if len(wordsSentence) < 60:
                                    frasina = cykParsing(wordsSentence, listProbPOS, nonTerminals, terminal)
                                    if frasina == "":
                                        frasina = "Non parsabile"
                                else:
                                    frasina = "Troppo lunga "+str(len(wordsSentence))
                                print(frasina)
                                
                                f = open("frasine2.txt", "a")
                                f.write(str(sentence)+"\n")
                                f.write(str(frasina)+"\n")
                                f.close()
                                c.append(frasina)
                                # Rilascio le risorse
                                #probPos = ""
                                #listProbPOS = ""
                        else:
                            print("Non ci sono parole in questa categoria di questa notizia")
                    n.append(c)
                newsParsed.append(n)
            print("Finito")
            pickle.dump(newsParsed, open(filename+".pcfg", "wb"))