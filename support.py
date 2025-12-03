import json
import zstandard as zstd
import numpy as np
import os
from PIL import Image



def DATATUPLE(data):
    if len(data)==0 :
        return []
    count=1
    compression=[]
    for i in range(1,len(data)):
        if(data[i-1]==data[i]):
            count+=1
        else:
            compression.append((data[i-1],count))
            count=1
    compression.append((data[-1],count))
    return compression



def RLEtexte(data):
    compression=''
    SUITETYPLE=DATATUPLE(data)
    max_occ = max(list(map(lambda x: x[1], SUITETYPLE))).bit_length()
    for value,count in SUITETYPLE:
        compression+=(format(ord(value), f"0{8}b"))
        compression+=(format(count, f"0{max_occ}b"))
    return max_occ,compression



def decodage_texte(datacompression):
    max_bit=datacompression[0]
    sequnce_bianiare=str(datacompression[1])
    segments=[]
    i=0
    while i < len(sequnce_bianiare):
        segments.append((chr(int(sequnce_bianiare[i:i+8],2))))
        i += 8
        if i < len(sequnce_bianiare):
            segments.append(str(int((sequnce_bianiare[i:i+max_bit]),2)))
            i += max_bit
    data = ""
    num = ""
    for indice in range(len(segments)):
        i = segments[indice]
        if i.isalpha() or i.isspace():
            data += i
        else:
            num += i
            if indice + 1 >= len(segments) or segments[indice + 1].isalpha() or segments[indice + 1].isspace():
                data += data[-1] * (int(num) - 1)
                num = ""
    return data



def RLE_bin(data):
    SUITETYPLE=DATATUPLE(data)
    max_occ = max(list(map(lambda x: x[1], SUITETYPLE))).bit_length()
    compression=''
    if(SUITETYPLE[0][0]==1):
        return max_occ,format(0, f"0{max_occ}b")+''.join(format(count, f"0{max_occ}b") for _,count in SUITETYPLE)
    else:
        return max_occ,''.join(format(count, f"0{max_occ}b") for _,count in SUITETYPLE) 



def decodage_bin(datacompression):
    max_bit = datacompression[0]
    sequence_binaire = datacompression[1]  
    
    data = [sequence_binaire[i:i+max_bit] for i in range(0, len(sequence_binaire), max_bit)]
    decimal_data = [int(i, 2) for i in data]
    
    liste = []
    current_value = 1 if decimal_data[0] == 0 else 0
    i = 1 if decimal_data[0] == 0 else 0
    
    for idx in range(i, len(decimal_data)):
        count = decimal_data[idx]
        liste.extend([current_value] * count)
        current_value = 1 - current_value
    return liste




def calc_freq(text):
    freq_dict = {}
    chars = set(text)
    for char in chars:
        freq_dict[char] = text.count(char)
    return dict(sorted(freq_dict.items(),key=lambda item : item[1]))



def huffmanC(dictio) :
    liste_symb = list(dictio.items())
    codage_dict = {car :"" for car,freq in liste_symb}
    while len(liste_symb) > 1 :
        min1 = min(liste_symb,key=lambda item:item[1])
        liste_symb.pop(liste_symb.index(min1))
        min2 = min(liste_symb,key=lambda item:item[1])
        liste_symb.pop(liste_symb.index(min2))
        for car in min1[0] :
            codage_dict[car] += "0" 
        for car in min2[0] :
            codage_dict[car] += "1"
        elem = [min1[0]+min2[0],min1[1]+min2[1]]
        liste_symb.append(elem)
    return {car  : code[::-1] for car,code in list(codage_dict.items())}



def sequenceBinaireHuffmanCodage(data):
    dictt = calc_freq(data)  
    dict_code = huffmanC(dictt) 
    return dict_code,"".join(dict_code[car] if isinstance(car, str) else dict_code[chr(car)] for car in data)



def decode_huffmane(encoded_seq):
    code_dictt=encoded_seq[0]
    rev_dict = {key: val for val, key in code_dictt.items()}  
    encodings = set(rev_dict.keys())  
    decoded_seq = []
    sequence = ""
    for bit in encoded_seq[1]:
        sequence += bit
        if sequence in encodings:  
            decoded_seq.append(rev_dict[sequence])  
            sequence = ""  
    return "".join(decoded_seq)



def LZ78_code(sequence):
    if isinstance(sequence, str):
        sequence = list(sequence)

    dico = {'' : 0}
    code = []
    n = 1

    while sequence:
        pre = ''
        for i, char in enumerate(sequence, start=1):
            if pre + char not in dico:
                code.append((dico[pre], char))
                dico[pre + char] = n
                break
            else:
                pre += char
        else:
            code.append((dico[pre], ''))
        
        del sequence[:i]
        n += 1
    
    return dico, code



def LZ78_decode(code):
    rev_dico = {}
    re_sequence = []
    for i,c in enumerate(code):
        if c[0] == 0:
            rev_dico[i+1] = c[1]
            re_sequence.append(c[1])
        else :
            re_sequence.append(rev_dico[c[0]] + c[1])
            rev_dico[i+1] = rev_dico[c[0]] + c[1]
    return re_sequence


def LZW_code(sequence):

    alphabet = {chr(i): i for i in range(256)}
    n = len(alphabet)
    min_seq = ""
    code = []
    point1, point2 = 0, 1

    while point2 <= len(sequence):
        seq = sequence[point1:point2]
        if seq in alphabet:
            min_seq = seq
            point2 += 1
        else:
            code.append(alphabet[min_seq])
            alphabet[seq] = n
            n += 1
            point1 = point2 - 1
            min_seq = ""
    
    if min_seq:
        code.append(alphabet[min_seq])

    return code



def LZW_code_bin(sequence):

    alphabet = {'0':0, '1':1}

    # alphabet = {'a':1,'c':2,'d':3,'e':4,'g':5,'i':6,'l':7,'m':8,'n':9,'o':10,'p':11,'r':12,'s':13,'t':14,'u':15,' ':16,',':17 }
    n = len(alphabet)
    min_seq = ""
    code = []
    point1, point2 = 0, 1

    while point2 <= len(sequence):
        seq = sequence[point1:point2]
        if seq in alphabet:
            min_seq = seq
            point2 += 1
        else:
            code.append(alphabet[min_seq])
            alphabet[seq] = n
            n += 1
            point1 = point2 - 1
            min_seq = ""
    
    if min_seq:
        code.append(alphabet[min_seq])

    return code



def LZW_decode(code):
    dict_LZW = []
    seq = []

    for elem in range(0, len(code) - 1):
        c1 = chr(code[elem]) if code[elem] <= 255 else dict_LZW[code[elem] - 256]
        if elem == 0 and code[elem + 1] > 255:
            c2 = chr(code[elem]) if code[elem] <= 255 else dict_LZW[code[elem] - 256]
        else:
            if code[elem + 1] - 256 < len(dict_LZW) or code[elem + 1] <= 255:
                c2 = chr(code[elem + 1]) if code[elem + 1] <= 255 else dict_LZW[code[elem + 1] - 256]
            else:
                c2 = c1
        seq.append(c1)
        dict_LZW.append(c1 + c2[0])
    seq.append(chr(code[-1]) if code[-1] <= 255 else dict_LZW[code[-1] - 256])

    return "".join(seq)



def LZW_decode_bin(code):
    dict_LZW = []
    seq = []
    chr = {0:'0',1:'1'}

    for elem in range(len(code) - 1):
        c1 = chr[code[elem]] if code[elem] <= 1 else dict_LZW[code[elem] - 2]
        if elem == 0 and code[elem + 1] > 1:
            c2 = chr[code[elem]] if code[elem] <= 1 else dict_LZW[code[elem] - 2]
        else:
            if code[elem + 1] - 2 < len(dict_LZW) or code[elem + 1] <= 1:
                c2 = chr[code[elem + 1]] if code[elem + 1] <= 1 else dict_LZW[code[elem + 1] - 2]
            else:
                c2 = c1
        seq.append(c1)
        dict_LZW.append(c1 + c2[0])
    seq.append(chr[code[-1]] if code[-1] <= 1 else dict_LZW[code[-1] - 2])

    return "".join(seq)



def codage_ligne(data):
    data=np.array(data)
    data = data.astype(int)
    ligne,colonne=data.shape
    liste=data.flatten()
    
    return liste,ligne,colonne



def de_ligne(liste,ligne,colonne):
    liste=np.array(liste)
    return liste.reshape((ligne, colonne))



def codage_colonne(data):
    data=np.array(data)
    data = data.astype(int)
    ligne,colonne=data.shape
    liste=data.T.flatten()
    return liste,ligne,colonne



def de_colonne(liste,ligne,colonne):
    liste=np.array(liste)
    return liste.reshape((colonne, ligne)).T



def codage_zigzag(data):
    resultat = []
    data = np.array(data)
    data = data.astype(int)
    ligne, cols = data.shape
    data = np.fliplr(data)
    for d in range(ligne + cols - 1):
        diagonal = np.diag(data, cols - d - 1)  
        if d % 2 == 0:
            resultat.extend(diagonal[::-1])  
        else:
            resultat.extend(diagonal)
    return np.array(resultat),ligne, cols



def de_zigzag(liste, rows, cols):
    matrice = np.zeros((rows, cols), dtype=int)
    index = 0
    liste = np.array(liste)
    for d in range(rows + cols - 1):
        if d < cols:
            i_start, j_start = 0, d
        else:
            i_start, j_start = d - cols + 1, cols - 1
        diag_indices = []
        while i_start < rows and j_start >= 0:
            diag_indices.append((i_start, j_start))
            i_start += 1
            j_start -= 1
        if d % 2 == 0:
            diag_indices.reverse()
        for i, j in diag_indices:
            matrice[i, j] = liste[index]
            index += 1
    return matrice



def sequnece_to_binairy(codage,nomfichier):
    json_data = json.dumps(codage).encode("utf-8")
    compressed_data = zstd.ZstdCompressor().compress(json_data)
    with open(f"{nomfichier}", "wb") as f:
        f.write(compressed_data)



def biniary_to_sequnece(nomfichier):
    with open(f"{nomfichier}", "rb") as f:
        decompressed_data = zstd.ZstdDecompressor().decompress(f.read())
    return json.loads(decompressed_data.decode("utf-8"))

def taux_reduction(original, compresse):
    taille1 = os.path.getsize(original)
    taille2 = os.path.getsize(compresse)
    return np.round((1 - taille2 / taille1) * 100, 2)

