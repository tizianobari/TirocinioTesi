#include <iostream>
#include <string>
#include <fstream>
#include <cuda.h>
#include <cuda_runtime.h>

using namespace std;

class Node {
    public:
        int symbol;
        string symbolStr;
        Node* left;
        Node* right;
        
        Node(int s)
        {
            this->symbol = s;
            this->left = NULL;
            this->right = NULL;
        }
        
        string listTree(string* nts, string* terminals, int &indexTerminals)
        {
            string list;
            
            list = "['" + nts[this->symbol] + "' ";
            
            if ( this->left != NULL )
            {
                list = list + ", ";
                list = list + (this->left)->listTree(nts, terminals, indexTerminals);
            }
            
            if ( this->right != NULL )
            {
                list = list + ", ";
                list = list + (this->right)->listTree(nts, terminals, indexTerminals);
            }
            
            if ( this->left == NULL && this->right == NULL ) 
            {
                list = list + string(", '") + terminals[indexTerminals] + string("'");
                indexTerminals = indexTerminals + 1;
            }
            
            list = list + "]";
            
            return list;
        }
};


bool fileExists(string filename)
{
    ifstream file(filename);
    bool exist = file.good();
    file.close();
    return exist;
}


// Verifica che 'symbol' sia presente nell'array dei simboli non terminali 'nts'
int getIndexNT(string symbol, string* nts, int nNT)
{
    int index = 0;
    string nt;
    bool found = false;
    while ( index < nNT && !found) 
    {
        nt = nts[index];
        //cout << "nonTerminals[" << index << "] = " << nt << "\n";
        if ( nt.compare(symbol) == 0 )
        {
            found = true;
        }
        else
        {
            index = index + 1;
        }
    }
    if ( !found )
    {
        index = -1;
    }
    return index;
}

// Funzione per dividere in un unico array la regola con posizione 0 leftside e le restanti due rightside
// Inutilizzata
// SI -> NP VP
// ai = 2,  lsi = 8
string* getSidesRule(string rule, int* numberRightSides)
{
    //cout << "Dentro la funzione per ottenere i dati della regola\n";
    int arrowIndex = 0;
    int lastSpaceIndex = 0;
    string arrow = " -> ";
    string space = " ";
    string rightSide1;
    string rightSide2;
    string leftSide;
    string* ruleSplitted;
    arrowIndex = rule.find(arrow);
    leftSide = rule.substr(0, arrowIndex);
    lastSpaceIndex = rule.rfind(space);
    if (lastSpaceIndex != arrowIndex+3)
    {
        //cout << "E' una regola binaria\n";
        // Se l'ultimo spazio non è quello dopo la freccia allora è una regola binaria
        (*numberRightSides) = 2;
        rightSide1 = rule.substr(arrowIndex+4, lastSpaceIndex-arrowIndex-4);
        rightSide2 = rule.substr(lastSpaceIndex+1);
    }
    else
    {
        //cout << "E' una regola unaria\n";
        // Altrimenti è una regola unaria
        (*numberRightSides) = 1;
        rightSide1 = rule.substr(arrowIndex+4);
    }
    
    //cout << "Numero di elementi a destra: " << (*numberRightSides) << "\n";
    
    ruleSplitted = new string[*(numberRightSides)+1];
    //cout << "Allocata l'array contenente gli elementi\n";
    if (*(numberRightSides) == 2)
    {
        ruleSplitted[0] = leftSide;
        ruleSplitted[1] = rightSide1;
        ruleSplitted[2] = rightSide2;
        //cout << "E' una regola binaria\n";
        //cout << "Regola sinistra: " << leftSide << "\n";
        //cout << "Regola destra prima: " << rightSide1 << "\n";
        //cout << "Regola destra seconda: " << rightSide2 << "\n";
        
    }
    else
    {
        ruleSplitted[0] = leftSide;
        ruleSplitted[1] = rightSide1;
        //cout << "E' una regola unaria\n";
        //cout << "Regola sinistra: " << leftSide << "\n";
        //cout << "Regola destra: " << rightSide1 << "\n";
    }
    return ruleSplitted;
}

__device__ void lock(int* mutex)
{
    /*printf("Lock!\n");
    while ( atomicCAS(mutex, 0, 1) != 0 );
    printf("Lockato con successo\n");*/
}

__device__ void unlock(int* mutex)
{
    /*printf("Unlock!\n");
    atomicExch(mutex, 0);
    printf("Unlockato con successo\n");*/
}



// Funzione kernel
__global__ void parsing(double* table, int* grammarsRules, double* grammarsProb, int nWords, int nGrammars, int nNT, int* back, int index, int split, int end)
{
    //printf("Entrato nel gpu thread\n");
    int leftSide;
    int rightSide1;
    int rightSide2;
    //int indexID = threadIdx.x;
    int indexID = blockIdx.x * blockDim.x + threadIdx.x;
    int stride = blockDim.x;
    double probSplitting;
    //pedix = 0;
    //int pedix = indexID;
    int pedix = 0;
    //cout << "Indice thread gpu: " << pedix << "\n";
    //printf("Indice thread gpu: %d \n", indexID);
    //printf("nWords, nGrammars, nNT -> %d %d %d \n", nWords, nGrammars, nNT);
    //while ( pedix < nGrammars )
    while ( pedix < nGrammars )
    {
        //printf("Sono nel while!\n");
        leftSide = grammarsRules[pedix*3];
        if ( leftSide == indexID )
        {
            rightSide1 = grammarsRules[(pedix*3)+1];
            rightSide2 = grammarsRules[(pedix*3)+2];
            //cout << "\t\t\t Regola sinistra: " << leftSide << "\n";
            //printf("%d: Regola: %d -> %d %d\n", indexID, leftSide, rightSide1, rightSide2);
            
            // Caso regola binaria
            if ( rightSide2 != -1 )
            {
                //lock(mutex);
                //cout << "\t\t\t E' una regola binaria " << leftSide << " -> " << rightSide1 << " " << rightSide2 << "\n";
                //printf("%d: E' una regola binaria %d -> %d %d \n", indexID, leftSide, rightSide1, rightSide2);
                //if ( table[index][split][rightSide1] != 0.0 && table[split+1][end][rightSide2] != 0.0 )
                //printf("Indici %d-%d-%d e %d-%d-%d  %d e %d e valori nella tabella del prossimo controllo: %f e %f \n", index, split, rightSide1, split+1, end, rightSide2, index + (nWords*split) + (nWords*nWords*rightSide1), split+1 + (nWords*end) + (nWords*nWords*rightSide2), table[index + (nWords*split) + (nWords*nWords*rightSide1)], table[split+1 + (nWords*end) + (nWords*nWords*rightSide2)]);
                if ( table[index + (nWords*split) + (nWords*nWords*rightSide1)] != 0.0 && table[split+1 + (nWords*end) + (nWords*nWords*rightSide2)] != 0.0 )
                {
                    //cout << "\t\t\t I simboli a destra hanno una probabilità diversa da zero \n";
                    //printf("\t\t\t I simboli a destra hanno una probabilità diversa da zero \n");
                    //probSplitting = grammarsProb[pedix] * table[index][split][rightSide1] * table[split+1][end][rightSide2];
                    probSplitting = grammarsProb[pedix] * table[index + (nWords*split) + (nWords*nWords*rightSide1)] * table[split+1 + (nWords*end) + (nWords*nWords*rightSide2)];
                    //if ( probSplitting > table[index][end][leftSide] )
                    if ( probSplitting > table[index + (end*nWords) + (leftSide*nWords*nWords)] )
                    {
                        //cout << "\t\t\t\t OK! della regola " << nonTerminals[leftSide] << " -> " << nonTerminals[rightSide1] << " " << nonTerminals[rightSide2] << "con probabilita: " << probSplitting << "\n";
                        //printf("\t\t\t\t %d : OK! della regola binaria %d -> %d %d \n", indexID, leftSide, rightSide1, rightSide2);
                        //table[index][end][leftSide] = probSplitting;
                        // Cambio con atomicMax?
                        table[index + (nWords*end) + (nWords*nWords*leftSide)] = probSplitting;
                        back[index + (end*nWords) + (nWords*nWords*leftSide) + (nNT*nWords*nWords*0)] = split;
                        back[index + (end*nWords) + (nWords*nWords*leftSide) + (nNT*nWords*nWords*1)] = rightSide1;
                        back[index + (end*nWords) + (nWords*nWords*leftSide) + (nNT*nWords*nWords*2)] = rightSide2;
                    }
                }
                //unlock(mutex);
            }
            // Caso regola unaria
            else if ( rightSide2 == -1 )
            {
                //indexRightSide1NT = getIndexNT(ruleSplitted[1], nonTerminals, nNT);
                //cout << "Indice nella tabella dei simboli non terminali del simbolo a destra: " << indexRightSide1NT << "\n";
                // Ignoro le regole unarie che portano ad un simbolo terminale perché le ho già studiate
                if ( rightSide1 != -1 && rightSide1 < nNT )
                {
                    //lock(mutex);
                    //cout << "\t\t\t E' una regola unaria senza simbolo terminale: " << nonTerminals[leftSide] << " -> " << nonTerminals[rightSide1] << "\n";
                    //printf("E' una regola unaria senza simbolo terminale: %d -> %d \n", leftSide, rightSide1);
                    //if ( table[index][split][rightSide1] != 0.0 )
                    //printf("Indice %d-%d-%d con indici totale %d e valore nella tabella nel prossimo controllo %f \n",index, split, rightSide1, index + (split*nWords) + (nWords*nWords*rightSide1), table[index + (split*nWords) + (nWords*nWords*rightSide1) ]);
                    if ( table[index + (split*nWords) + (nWords*nWords*rightSide1) ] != 0.0 )
                    {
                        //probSplitting = grammarsProb[pedix] * table[index][split][rightSide1];
                        probSplitting = grammarsProb[pedix] * table[index + (split*nWords) + (nWords*nWords*rightSide1)];
                        //if ( probSplitting > table[index][split][leftSide] )
                        if ( probSplitting > table[index + (split*nWords) + (nWords*nWords*leftSide) ] )
                        {
                            //cout << "\t\t\t\t OK! della regola unaria " << nonTerminals[leftSide] << " -> " << nonTerminals[rightSide1] << " con probabilita: " << probSplitting << "\n";
                            //printf("\t\t\t\t %d : OK! della regola unaria %d -> %d\n", indexID, leftSide, rightSide1);
                            //table[index][split][leftSide] = probSplitting;
                            table[index + (split*nWords) + (nWords*nWords*leftSide)] = probSplitting;
                            back[index + (split*nWords) + (nWords*nWords*leftSide) + (nNT*nWords*nWords*0)] = split;
                            back[index + (split*nWords) + (nWords*nWords*leftSide) + (nNT*nWords*nWords*1)] = rightSide1;
                            back[index + (split*nWords) + (nWords*nWords*leftSide) + (nNT*nWords*nWords*2)] = -1;
                            
                        }
                    }
                    //unlock(mutex);
                }
            }
        }
        //cout << "passo alla regola successiva\n";
        pedix = pedix + 1;
        
        //pedix = pedix + stride;
    }
}



// Array di parole con relativa dimensione
// Array delle regole delle grammatiche con relativa dimensione
// Array delle probabilità delle regole della grammatica
// Array dei simboli non terminali con relativa dimensione
// Matrice per ottenere l'albero passata per riferimento?
int* cykParsing(string* words, int nWords, int* grammarsRules, int nGrammars, double* grammarsProb, string* nonTerminals, int nNT, string* terminals, int nTerminals)
{
    //double*** table;
    double* table;
    int* back;
    // Memoria device
    double* tableDevice;
    int* backDevice;
    //int* nWordsDevice;
    //int* nGrammarsDevice;
    double* grammarsProbDevice;
    int* rulesDevice;
    int* mutex;
    int state = 0;
    
    //double*** back;
    int i;
    int j;
    int k;
    int index;
    int pedix;
    int numberRightSides;
    
    //string* ruleSplitted;
    int leftSide;
    int rightSide1;
    int rightSide2;
    
    //int* rule;
    double probSplitting;
    int length;
    int split;
    int end;
    // Iterazione per inizializzare la matrice contenente le probabilità delle grammatiche
    cout << "Cykparsing - creazione matrici\n";
    table = new double[nWords*nWords*nNT];
    back = new int[nWords*nWords*nNT*3];
    i = 0;
    while ( i < nWords*nWords*nNT )
    {
        table[i] = 0.0;
        i = i + 1;
    }
    
    i = 0;
    while ( i < nWords*nWords*nNT*3 )
    {
        back[i] = -1;
        i = i + 1;
    }
    

    cout << "Cykparsing - matrici create\n";
    // Inizializzazione matrici con probabilità delle regole X -> xi delle parole
    // index indice delle parole ; pedix indice delle grammatiche
    cout << "inizializzazione matrici con probabilità delle parole\n";
    index = 0;
    while ( index < nWords ) 
    {
        pedix = 0;
        while ( pedix < nGrammars )
        {
            //cout << "\t "<< index << ": studio regola " << rule << " " << rule[0] << " " << rule[1] << " " << rule[2] << "\n";
            //ruleSplitted = getSidesRule(rule, &numberRightSides);
            leftSide = grammarsRules[pedix*3];
            rightSide1 = grammarsRules[(pedix*3)+1];
            rightSide2 = grammarsRules[(pedix*3)+2];
            
            if ( rightSide2 == -1 && rightSide1 >= nNT && words[index].compare(terminals[rightSide1-nNT]) == 0 )
            {
                //table[index][index][leftSide] = grammarsProb[pedix];
                table[index + (nWords*index) + (leftSide*nWords*nWords)] = grammarsProb[pedix];
                //cout << "\tSettato nella tabella con indice " << index << "-" << index << "-" << leftSide << " e indice totale " << index + (nWords*index) + (leftSide*nWords*nWords) << " e regola: "<< nonTerminals[leftSide] << " -> " << terminals[rightSide1-nNT] << " con valore :" << grammarsProb[pedix] << "=" << table[index + (nWords*index) + (leftSide*nWords*nWords)] << "\n";
            }
            pedix = pedix + 1;
        }
        index = index + 1;
    }
    
    
     // Allocazione memoria device
    /*    // Memoria device
        double* tableDevice;
        int* nWordsDevice;
        int* nGrammarsDevice;
        double* grammarsProbDevice;*/
    cudaMalloc((void**)&tableDevice, sizeof(double)*nWords*nWords*nNT);
    cudaMalloc((void**)&backDevice, sizeof(int)*nWords*nWords*nNT*3);
    ///cudaMalloc((void**)&nWordsDevice, sizeof(int));
    ///cudaMalloc((void**)&nGrammarsDevice, sizeof(int));
    cudaMalloc((void**)&grammarsProbDevice, sizeof(double)*nGrammars);
    cudaMalloc((void**)&rulesDevice, sizeof(int)*nGrammars*3);
    //cudaMalloc((void**)&mutex, sizeof(int));
    
    
    // Copia dati da memoria host a memoria device
    cudaMemcpy(tableDevice, table, sizeof(double)*nWords*nWords*nNT, cudaMemcpyHostToDevice);
    //cudaMemcpy(nWordsDevice, &nWords, sizeof(int), cudaMemcpyHostToDevice);
    //cudaMemcpy(nGrammarsDevice, &nGrammars, sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy(grammarsProbDevice, grammarsProb, sizeof(double)*nGrammars, cudaMemcpyHostToDevice);
    cudaMemcpy(rulesDevice, grammarsRules, sizeof(int)*nGrammars*3, cudaMemcpyHostToDevice); 
    //cudaMemcpy(mutex, &state, sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy(backDevice, back, sizeof(int)*nWords*nWords*nNT*3, cudaMemcpyHostToDevice);
    
    cout << "Dimensioni nWords, nGrammars, nNT : " << nWords << " " << nGrammars << " " << nNT;
    
    length = 1;
    // index, split, end per la matrice
    // pedix per le grammatiche
    while ( length < nWords )
    {
        index = 0;
        while ( index < nWords - length )
        {
            end = index + length;
            split = index;
            while ( split < end ) 
            {   
                ///cout << "\t Studio la regola binaria con sottostringhe pari a : " << index << "-" << split << " e " << split+1 << "-" << end << "\n";
                //parsing(double* table, int* grammarsRules, double* grammarsProb, int nWords, int nGrammars, int nNT,  int index, int split, int end)
                // block_size = 256 grid_size = N+block_size  / block_size
                parsing<<<8,256>>>(tableDevice, rulesDevice, grammarsProbDevice, nWords, nGrammars, nNT, backDevice, index, split, end);
                cudaDeviceSynchronize();
                split = split + 1;
            } 
            index = index + 1;
        }
        length = length + 1;
    }
    //cout << "Dopo i gpu threading\n";
    
    int indexStartSymbol;
    string startSymbol = "S";
    indexStartSymbol = getIndexNT(startSymbol, nonTerminals, nNT);
    
    //cout << "Ottenuto il simbolo di inizio frase " << indexStartSymbol << "\n";
    
    // Trasferisco i dati dalla memoria device alla memoria host
    cudaMemcpy(table, tableDevice, sizeof(double)*nWords*nWords*nNT, cudaMemcpyDeviceToHost);
    cudaMemcpy(back, backDevice, sizeof(int)*nWords*nWords*nNT*3, cudaMemcpyDeviceToHost);
    
    cout << "------PROBABILITA PARSING : " << table[0 + (nWords*(nWords-1)) + (indexStartSymbol*nWords*nWords)] << "\n";
    cudaFree(tableDevice);
    cudaFree(grammarsProbDevice);
    cudaFree(rulesDevice);
    cudaFree(backDevice);
    //cudaFree(mutex);
    //return table[0 + (nWords*(nWords-1)) + (indexStartSymbol*nWords*nWords)];
    if ( table[0 + (nWords*(nWords-1)) + (indexStartSymbol*nWords*nWords)] == 0.0 )
    {
        cout << "Tabella == 0 cancello\n";
        delete[] back;
        back = NULL;
    }
    delete[] table;
    return back;
}




// Procedura per leggere la grammatica dal file, nei parametri passa l'array delle regole e delle probabilità
int readGrammar(ifstream &file, int* &rules, double* &probs)
{
    string line;
    int nLines = 0;
    int index;
    
    int indexTab;
    int indexFirstSpace;
    int indexSecondSpace;
    
    int firstSymbol;
    int secondSymbol;
    int thirdSymbol;
    
    double prob;
    
    // Verifico quante regole ci sono nel file per allocare la memoria
    if ( file.is_open() )
    {
        // Prima riga è il numero di grammatiche
        getline(file, line);
        nLines = atoi(line.c_str());
        
        // Allocazione in memoria degli array per memorizzare i dati
        rules = new int[nLines*3];
        probs = new double[nLines];
        index = 0;
        while ( index < nLines )
        {
            rules[index*3] = 0;
            rules[(index*3)+1] = 0;
            rules[(index*3)+2] = 0;
            probs[index] = 0.0;
            index = index + 1;
        }
        
        index = 0;
        while ( getline(file, line) )
        {
            // La riga è composta da int int int[tabulazione]double
            indexTab = line.find("\t");
            // Dall'indice della tabulazione a fine riga c'è il double
            indexFirstSpace = line.find(" ");
            indexSecondSpace = line.find(" ", indexFirstSpace+1);
            
            firstSymbol = atoi(line.substr(0, indexFirstSpace).c_str());
            secondSymbol = atoi(line.substr(indexFirstSpace+1, indexSecondSpace-indexFirstSpace).c_str());
            thirdSymbol = atoi(line.substr(indexSecondSpace+1, indexTab-indexSecondSpace).c_str());
            //cout << "Il terzo simbolo della grammatica e' : " << thirdSymbol << "\n";
            prob = atof(line.substr(indexTab+1).c_str());
            
            rules[index*3] = firstSymbol;
            rules[(index*3)+1] = secondSymbol;
            rules[(index*3)+2] = thirdSymbol;
            
            //cout << "Il terzo simbolo della grammatica e' : " << thirdSymbol << " = " << rules[(index+3)+2] << " \n";
            
            probs[index] = prob;
            
            index = index + 1;
        }
        
        file.close();
    }
    else
    {
        cout << "Non è stato possibile aprire il file\n";
    }
    return nLines;
}

int readNonTerminals(ifstream &file, string* &nonTerminals)
{
    string line;
    int nLines;
    int index; 
    
    if ( file.is_open() )
    {
        // Ottengo il numero di grammatiche presenti nel file
        getline(file, line);
        nLines = atoi(line.c_str());
        
        // Allocazione memoria
        nonTerminals = new string[nLines];
        
        index = 0;
        while ( getline(file, line) )
        {
            //cout << "secondo giro non terminale = " << line << "\n";
            nonTerminals[index] = line;
            index = index + 1;
        }
        //cout << "Numero di non terminali trovati : " << nLines << "\n";
        file.close();
    }
    else
    {
        cout << "Errore durante l'apertura del file\n";
    }
    return nLines;
}

int* joinArray(int* array1, int* array2, int size1, int size2)
{
    int* total = new int[(size1+size2)*3];
    int index;
    int pedix;
    
    index = 0;
    pedix = 0;
    cout << "Inserisco l'array2 in total\n";
    while ( pedix < size2 )
    {
        //cout << "\t " << index << " = " << pedix << "\n";
        total[(index*3)] = array2[(pedix*3)];
        total[(index*3)+1] = array2[(pedix*3)+1];
        total[(index*3)+2] = array2[(pedix*3)+2];
        //cout << "\t " << total[index*3] << " = " << array2[pedix*3] << "\n";
        index = index + 1;
        pedix = pedix + 1;
    }
    cout << "Finito l'array2 ora l'indice è: " << index << "\n";
    cout << "Inserisco l'array1 in total\n";
    pedix = 0;
    while ( pedix < size1 )
    {
        //cout << "\t " << index*3 << " = " << pedix*3 << "\n";
        total[(index*3)] = array1[(pedix*3)];
        total[(index*3)+1] = array1[(pedix*3)+1];
        total[(index*3)+2] = array1[(pedix*3)+2];
        //cout << "\t " << total[(index*3)+2] << " = " << array1[(pedix*3)+2] << "\n";
        index = index + 1;
        pedix = pedix + 1;
    }
    cout << "Dimensioni array: " << size1 << " " << size2 << "\n";
    return total;
}

double* joinArray(double* array1, double* array2, int size1, int size2)
{
    double* total = new double[size1+size2];
    int index;
    int pedix;
    
    index = 0;
    pedix = 0;
    cout << "Inserisco l'array2 in total\n";
    while ( pedix < size2 )
    {
        //cout << "\t " << index << " = " << pedix << "\n";
        total[index] = array2[pedix];
        //cout << "\t " << total[index] << " = " << array2[pedix] << "\n";
        index = index + 1;
        pedix = pedix + 1;
    }
    
    pedix = 0;
    while ( pedix < size1 )
    {
        //cout << "\t " << index << " = " << pedix << "\n";
        total[index] = array1[pedix];
        //cout << "\t " << total[index] << " = " << array1[pedix] << "\n";
        index = index + 1;
        pedix = pedix + 1;
    }
    return total;
}

int readWords(ifstream &file, string* &words)
{
    string line;
    int nWords;
    int index;
    int start;
    int end;
    // La prima riga contiene il numero di parole della frase
    getline(file, line);
    nWords = atoi(line.c_str());
    
    words = new string[nWords];
    getline(file, line);
    
    index = 0;
    start = 0;    
    while ( index < nWords )
    {
        end = line.find("\t", start+1);
        if ( end != -1 )
        {
            words[index] = line.substr(start, end-start);
            start = end + 1;
        }
        else
        {
            // Ultima parola
            words[index] = line.substr(start);
        }
        index = index + 1;
    }
    return nWords;
}

int readTerminals(ifstream &file, string* &terminals)
{
    string line;
    int nTerminals;
    int index;
    int start;
    int end;
    // La prima riga contiene il numero di simboli terminali
    getline(file, line);
    nTerminals = atoi(line.c_str());
    
    terminals = new string[nTerminals];
    getline(file, line);
    
    index = 0;
    start = 0;    
    while ( index < nTerminals )
    {
        end = line.find("\t", start+1);
        if ( end != -1 )
        {
            terminals[index] = line.substr(start, end-start);
            start = end + 1;
        }
        else
        {
            // Ultima parola
            terminals[index] = line.substr(start);
        }
        index = index + 1;
    }
    return nTerminals;
}

void printTree(Node* tree, int level, string* nts, string* terminals, int &indexTerminals)
{
    int index = 0;
    while ( index < level )
    {
        cout << "\t";
        index = index + 1;
    }
    
    //cout << "[";
    cout << nts[tree->symbol];
    if ( tree->left != NULL )
    {
        printTree(tree->left, level+1, nts, terminals, indexTerminals);
    }

    
    if ( tree->right != NULL )
    {
        printTree(tree->right, level+1, nts, terminals, indexTerminals);
    }
    
    if ( tree->left == NULL && tree->right == NULL )
    {
        // Terminale
        cout << "\t" << terminals[indexTerminals];
        indexTerminals = indexTerminals + 1;
    }
    cout << "\n";
    //cout << "]";
}

// Inizio con start = 0, end = nWords-1, symbol = 'S' (indice)
Node* getTree(int* back, int nWords, int nNT, int start, int end, int symbol)
{
    int split;
    int left;
    int right;
    Node* tree = new Node(symbol);
    //cout << "Il nodo ha valore: " << symbol << "\n";
    split = back[start + (end*nWords) + (nWords*nWords*symbol) + (nNT*nWords*nWords*0)];
    if  ( split != -1 )
    {
        // Verifica se è ha un unico figlio o due 
        left = back[start + (end*nWords) + (nWords*nWords*symbol) + (nNT*nWords*nWords*1)];
        right = back[start + (end*nWords) + (nWords*nWords*symbol) + (nNT*nWords*nWords*2)];
        
        tree->left = getTree(back, nWords, nNT, start, split, left);
        // Se era una regola binaria ha anche il secondo figlio
        if ( right != -1 )
        {
            tree->right = getTree(back, nWords, nNT, split+1, end, right);
        }
    }

    return tree;
}


void divideLineWords(string line, string* words, int* tags, int nWords)
{
    
}

/*int readNews(ifstream fileNews, string** newsTitles, int** tagTitles, string** newsSubtitles, int** tagSubtitles , string** newsCorpus, int** tagCorpus)
{
    string line;
    string title;
    string subtitle;
    string corpus;
    int nNews;
    int index;
    int nWordsTitle;
    int nWordsSubtitle;
    int nWordsCorpus;
    
    
    if ( file.is_open() )
    {
        // La prima riga contiene il numero di notizie totali
        getline(file, line);
        nNews = atoi(line.c_str());
        
        // Allocazione matrice per contenere le parole e i tag
        newsTitles = new string*[nNews];
        newsSubtitles = new string*[nNews];
        newsCorpus = new string*[nNews];
        tagTitles = new int*[nNews];
        tagSubtitles = new int*[nNews];
        tagCorpus = new int*[nNews];
        
        index = 0;
        while ( index < nNews )
        {
            // Ogni notizia ha 6 righe: 3 categorie con 2 righe per numero parole e parole con i tag
            getline(file, line);
            nWordsTitle = atoi(nWordsTitle.c_str());
            newsTitles[index] = new string[nWordsTitle];
            tagTitles[index] = new int[nWordsTitle];
            getline(file, title);
            
            getline(file, line);
            nWordsSubtitle = atoi(nWordsSubtitle.c_str());
            newsSubtitles = new string[nWordsSubtitle];
            tagSubtitles = new int[nWordsSubtitle];
            getline(file, subtitle);
            
            getline(file, line);
            nWordsCorpus = atoi(nWordsCorpus.c_str());
            newsCorpus = new string[nWordsCorpus];
            tagCorpus = new int[nWordsCorpus];
            
            // parola tag \t parola ...
            // Ottengo le parole e i tag 
            index = index + 1;
        }
    }
    else
    {
        cout << "Errore durante l'apertura del file contenente le notizie\n";
    }
}*/

// Manca la procedura per ottenere l'albero
// L'albero array di oggetti?
// Le grammatiche nel file di testo divise da una tabulazione e \n
// 

string getNameCategory(int category)
{
    string cat;
    if ( category == 0 )
    {
        cat = "title";
    }
    if ( category == 1 )
    {
        cat = "subtitle";
    }
    if ( category == 2 )
    {
        cat = "corpus";
    }       
    return cat;
}


int main(int na, char **va)
{   
    // Array per le regole, probabilita, parole, simboli non terminali e simboli terminali
    int* rules;
    double* probs;
    string* words;
    string* nts;
    string* terminals;
    int* rulesTerminals;
    double* probsTerminals;
    int* rulesTotal;
    double* probsTotal;
    // Relative dimensioni
    int nGrammars;
    int nNT;
    int nWords;
    int nTerminalsGrammars;
    int nTerminals;
    int nTotalGrammars;
    // Variabili per navigare attraverso le notizie categorie e frasi
    int nNews;
    int category;
    int index;
    string* text;
    
    int v;
    int* parsed;
    string startSymbol = "S";
    int indexParsing = 0;
    // indice frasi e stringhe per passaggio da intero a stringa
    int indexSentence;
    char strIndexSentence[6];
    char strIndexNews[6];
    // Variabili per aprire i file
    string pathSentence;
    string pathParsed;
    string treeParsed;
    
    ifstream fileSentence;
    ifstream fileNT;
    ifstream fileGrammars;
    ofstream fileParsed;
    
    fileNT.open("politifact.nt.txt");
    fileGrammars.open("general.grammars.txt");
    
    cout << "Ottengo grammatiche di base\n";
    nGrammars = readGrammar(fileGrammars, rules, probs);
    cout << "Grammatiche di base lette\n";
    
    v = 0;
    while ( v < nGrammars ) 
    {
        //cout << "rules[" << v << "] = " << rules[v*3] << " " << rules[(v*3)+1] << " " << rules[(v*3)+2] << "\n";
        v = v + 1;
    }
    
    cout << "Ottengo i simboli non terminali\n";
    nNT = readNonTerminals(fileNT, nts);
    cout << "Simboli non terminali ottenuti\n";
    
    // Costante politifact
    nNews = 947;
    // Iterazione per effettuare il parsing delle frasi
    index = 295;
    while ( index <= nNews )
    {
        cout << "Prendo in considerazione la notizia " << index << "\n";
        category = 0;
        // Numero di categoria indica rispettivamente titolo sottotitolo e corpus
        while ( category < 3 )
        {
            cout << "\t con categoria " << category << "\n";
            indexSentence = 0;
            while ( indexSentence != -1 )
            {
                cout << "\t\t frase " << indexSentence << "\n";
                sprintf(strIndexSentence, "%d", indexSentence);
                sprintf(strIndexNews, "%d", index);
                
                pathSentence = "politifact/"+string(strIndexNews);
                pathSentence = pathSentence + "."+getNameCategory(category)+".";
                pathSentence = pathSentence + string(strIndexSentence)+".txt";
                
                pathParsed = "parsed/politifact/"+string(strIndexNews);
                pathParsed = pathParsed + "."+getNameCategory(category)+".";
                pathParsed = pathParsed + string(strIndexSentence)+".parsed";
    
                fileSentence.open(pathSentence);
                
                if ( fileSentence.is_open() )
                {
                    if ( !fileExists(pathParsed) )
                    {
                        // Prime due righe relative al numero di parole
                        //cout << "Leggo le parole della frase\n";
                        nWords = readWords(fileSentence, words);
                        // Segmentation fault se il numero di parole è troppo alto
                        if ( nWords <= 100 )
                        {
                            //cout << "Lette le parole \n";
                            // altre due righe relative al numero di simboli non terminali
                            // cout << "Leggo i simboli terminali della frase \n";
                            nTerminals = readTerminals(fileSentence, terminals);
                            //cout << "Letti i simboli terminali della frase \n";
                            // Il resto per le grammatiche
                            //cout << "Leggo le grammatiche dei simboli terminali della frase \n";
                            nTerminalsGrammars = readGrammar(fileSentence, rulesTerminals, probsTerminals);
                            //cout << "Lette le grammatiche dei simboli terminali della frase \n";
                            // Istanze per le grammatiche totali
                            //cout << "Unisco le regole \n";
                            rulesTotal = joinArray(rules, rulesTerminals, nGrammars, nTerminalsGrammars);
                            //cout << "Finito di unire le regole\n";
                            //cout << "Unisco le probabilita \n";
                            probsTotal = joinArray(probs, probsTerminals, nGrammars, nTerminalsGrammars);
                            //cout << "Finito di unire le probabiltia \n";
                            nTotalGrammars = nGrammars+nTerminalsGrammars;
                          
                            v = 0;
                            while ( v < nWords )
                            {
                                //cout << "words[" << v << "] = " << words[v] << "\n";
                                v = v + 1;
                            }
                            
                            v = 0;
                            while ( v < nTerminals )
                            {
                                //cout << "terminals[" << v << "] = " << terminals[v] << "\n";
                                v = v + 1;
                            }
                            
                            v = 0;
                            while ( v < nNT )
                            {
                                //cout << "nonTerminals[" << v << "] = " << nts[v] << "\n";
                                v = v + 1;
                            }
                            
                            v = 0;
                            while ( v < nTotalGrammars ) 
                            {
                                //cout << "totalRules[" << v << "] = " << rulesTotal[v*3] << " " << rulesTotal[(v*3)+1] << " " << rulesTotal[(v*3)+2] << "\n";
                                v = v + 1;
                            }
                            
                            // Esecuzione del parsing
                            cout << "Inizio parsing! "<< pathSentence << "\n";
                            parsed = cykParsing(words, nWords, rulesTotal, nTotalGrammars, probsTotal, nts, nNT, terminals, nTerminals);
                            if ( parsed != NULL )
                            {                    
                                cout << "Percorso file parsato: " << pathParsed << "\n";
                                fileParsed.open(pathParsed);
                                //cout << "Aperto il file \n";
                                indexParsing = 0;
                                treeParsed = getTree(parsed, nWords, nNT, 0, nWords-1, getIndexNT(startSymbol, nts, nNT))->listTree(nts, words, indexParsing);
                                cout << treeParsed << "\n";
                                fileParsed << treeParsed;
                                fileParsed.close();
                                
                                delete[] parsed;
                            }
                            else
                            {
                                fileParsed.open(pathParsed);
                                fileParsed << "No parsing";
                                fileParsed.close();
                            }
                            // Deallocazione e passaggio alla frase successiva
                            cout << "Deallocazione memoria\n";
                            delete[] rulesTotal;       
                            delete[] probsTotal;
                            cout << "Deallocazione terminali\n";
                            delete[] terminals;
                            cout << "Deallocazione roba terminale\n";
                            delete[] rulesTerminals;
                            delete[] probsTerminals;
                        }
                        else
                        {
                            cout << "Frase troppo lunga: " << nWords << "\n";
                            fileParsed.open(pathParsed);
                            fileParsed << "Lunga";
                            fileParsed.close();
                        }
                        // Deallocazione e passaggio alla frase successiva
                        //cout << "Deallocazione memoria\n";
                        // segfault
                        //delete rulesTotal;

                        cout << "Deallocazione words terminals\n";
                        delete[] words;
                    }
                    else
                    {
                        cout << "File è stato già parsato: " << pathParsed << "\n";
                    }
                                            
                    cout << "Chiudo il file contenente la notizia \n";
                    // Salvare il parsing da qualche parte
                    
                    fileSentence.close();
                    indexSentence = indexSentence + 1;
                    cout << "Passo alla frase successiva\n";
                }
                else
                {
                    cout << "Non esiste il file " << pathSentence << "\n";
                    // Passo alla categoria successiva visto che il file non esiste
                    category = category + 1;
                    indexSentence = -1;
                }
            }
        }
        index = index +1;
    }
    fileNT.close();
    fileGrammars.close();
    delete nts;
    delete probs;
    delete rules;
    //cykParsing(String* words, int nWords, String* grammarsRules, int nGrammars, double* grammarsProb, String* nonTerminals, int nNT)
    //prob = cykParsing(words, nWords, rules, nRules, probs, nts, nNT, terminals, nTerminals);
}