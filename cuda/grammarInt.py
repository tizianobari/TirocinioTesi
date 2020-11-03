import pickle

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


generalGrammars = pickle.load(open("../dataset/general.grammars", "rb"));
nts = pickle.load(open("../dataset/politifact.csv.2.pos.nt", "rb"));

grammarsInt = []
grammarsProb = []

for index in range(len(list(generalGrammars.keys()))):
    rule = list(generalGrammars.keys())[index]
    prob = generalGrammars[rule]
    ruleInt = []
    
    
    ruleSplitted = getSidesRule(rule)
    
    leftSide = ruleSplitted[0]
    rightSide = ruleSplitted[1]
    
    ruleInt.append(nts.index(leftSide))
    ruleInt.append(nts.index(rightSide[0]))
    if len(rightSide) == 2:
        ruleInt.append(nts.index(rightSide[1]))
    else:
        ruleInt.append(-1)
        
    grammarsProb.append(prob)
    grammarsInt.append(ruleInt)
    
fileGrammars = open("general.grammars.txt","w")
fileNT = open("politifact.nt.txt", "w")
for index in range(len(grammarsInt)):
    fileGrammars.write(str(grammarsInt[index][0])+" "+str(grammarsInt[index][1])+" "+str(grammarsInt[index][2])+"\t"+str(grammarsProb[index]))
    if index+1 != len(grammarsInt):
        fileGrammars.write("\n")
        
for index in range(len(nts)):
    fileNT.write(nts[index])
    if index+1 != len(nts):
        fileNT.write("\n")

fileGrammars.close()
fileNT.close()
