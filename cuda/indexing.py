grammarsIndexed = []
for rule in rules:
    splitted = getSidesRule(rule)
    leftSide = splitted[0]
    rightSide = splitted[1]
    indexed = []
    indexed.append(nonTerminals.index(leftSide))
    if rightSide[0] in nonTerminals:
        indexed.append(nonTerminals.index(rightSide[0]))
    else:
        indexed.append(terminals.index(rightSide[0])+len(nonTerminals))
    if len(rightSide) == 2:
        if rightSide[1] in nonTerminals:
            indexed.append(nonTerminals.index(rightSide[1]))
        else:
            indexed.append(terminals.index(rightSide[0])+len(nonTerminals))
    else:
        indexed.append(-1)
        
    grammarsIndexed.append(indexed)
    