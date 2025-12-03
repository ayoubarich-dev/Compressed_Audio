from collections import Counter
import numpy as np
import pickle

def getBitLength(data):
    """Determine the minimum bit length required to store the maximum value in data."""
    max_value = max(int(val) for val in data) if isinstance(data, (np.ndarray, list)) else max(ord(char) for char in data)
    return max_value.bit_length()

def dataToBinary(data):
    bit_length=getBitLength(data)
    if isinstance(data, str):
        binary_form= np.array([format(ord(car), f"0{bit_length}b") for car in data])
    else:
        binary_form = np.array([format(car, f"0{bit_length}b") for car in data])
    binary = ''.join(binary_form.astype(str))
    return binary, bit_length

def st(suites_symboles):
    suite_tuples=[]
    count=1
    for i in range(len(suites_symboles)):
        symbole=suites_symboles[i]
        next_symbole=suites_symboles[i+1] if i+1<len(suites_symboles) else None
        if next_symbole==symbole:
            count+=1
        else:
            suite_tuples.append([symbole,count])
            count=1
    return suite_tuples
def RLE_v1(suites_symboles,type):
    suite_tuples=st(suites_symboles)
    code_RLE=''
    if type=="word":
        for sublist in suite_tuples:
            if sublist[1]==1:
                code_RLE+=str(suite_tuples[0]).upper()
            else:
                code_RLE+=str(suite_tuples[1])+str(suite_tuples[0]).upper()
    if type=="bin":
        code_RLE=""
        if suite_tuples[0][0]=="0":
                code_RLE+="1"
        else:
            code_RLE+="0"
        for sublist in suite_tuples:
            code_RLE+=str(sublist[1])
    return code_RLE,suite_tuples

def RLE(suites_symboles):
    suite_tuples = st(suites_symboles)
    code_RLE = ''
    max_freq = max(suite_tuples, key=lambda x: x[1])[1]
    coding_bit_length = max_freq.bit_length()
    code_RLE = "1" if suite_tuples[0][0] == "0" else "0"
    for sublist in suite_tuples:
        code_RLE += format(sublist[1], f'0{coding_bit_length}b') 
    return code_RLE,coding_bit_length

def RLE_img_horiz(img_array):
    sequence=img_array.flatten()
    string_sequence,first_bit_length=dataToBinary(sequence)
    compressed_string,second_bit_length=RLE(string_sequence)
    return string_sequence,compressed_string,first_bit_length,second_bit_length

def RLE_img_vert(img_array):
    sequence=img_array.flatten(order='F')
    string_sequence,first_bit_length=dataToBinary(sequence)
    compressed_string,second_bit_length=RLE(string_sequence)
    return string_sequence,compressed_string,first_bit_length,second_bit_length

def RLE_img_zig(image_array):
    img_array=image_array.copy()
    
    if len(img_array.shape) == 2:  # Grayscale image (2D)
        M, N = img_array.shape
        D = 1  # Only one channel
        img_array = img_array[..., np.newaxis]
    else:  # RGB image (3D)
        M, N, D = img_array.shape
    mn = min(M, N)
    Mx = max(M, N)
    print("size lwl",M*N*D)
    nbr_diags=0
    # Prepare for storing the zigzag sequences
    zigzag_sequence_arr = []
    
    
    # Loop over each diagonal and process zigzag
    for d in range(D):
        img_array[:,:,d] = np.fliplr(img_array[:,:,d])
        flip = 1  # Variable to track flip state
        for i in range(Mx - 1, -(mn), -1):
            sequence = img_array[:, :, d].diagonal(i)  # Get the diagonal for channel d
            if flip % 2:
                sequence = np.flip(sequence)  # Flip the sequence
            zigzag_sequence_arr = np.append(zigzag_sequence_arr, sequence)
            flip += 1
            nbr_diags+=1
    zigzag_sequence_arr = zigzag_sequence_arr.flatten().astype(int)  # Flatten and convert to int
    zigzag_sequence_str, first_bit_length = dataToBinary(zigzag_sequence_arr)  # Convert to binary string
    compressed_string, second_bit_length = RLE(zigzag_sequence_str)  # Perform RLE
    
    return zigzag_sequence_str, compressed_string, first_bit_length, second_bit_length


def taux_comp(initial, final):
    initial_size = len(initial)
    final_size= len(final)
    taux = (1 - (final_size / initial_size)) * 100
    print(final_size,initial_size)
    print(f"Le taux de compression est {taux:.2f}%")
    return taux

def taux_comp_v1(initial, tuple_set, type):
    tuple_set = np.array(tuple_set, dtype=object)  # Ensure it's an array of tuples
    second_col = tuple_set[:, 1].astype(int)  # Extract frequency counts
    ones = np.count_nonzero(second_col == 1)
    twos = np.count_nonzero(second_col == 2)
    rest = len(tuple_set) - ones - twos  # Remaining elements
    MAX_freq = int(np.max(second_col) if len(second_col) > 0 else 1)  # Avoid errors
    if type == "bin":
        initial_size = len(initial)
        # Binary encoding: 2-bit for ones, 4-bit for twos, and MAX_freq.bit_length() for others
        size = (ones * 2) + (twos * 2) + (rest * (MAX_freq.bit_length()))
    elif type == "word":
        initial_size = len(initial) * 8 
        # Word encoding: Single characters are stored as 1 char, numbers as MAX_freq.bit_length()
        size = (ones * 8) + (twos * 16) + (rest * (8 + MAX_freq.bit_length()))
    else:
        raise ValueError("Invalid type! Use 'bin' or 'word'.")
    taux = (1 - (size / initial_size)) * 100
    print(size,initial_size)
    print(f"Le taux de compression est {taux:.2f}%")
    return taux



def decoder_RLE(code_RLE, type,first_bit_length,second_bit_length):
    suites_bin = ''
    i = 1
    curr = "1" if code_RLE[0] == "0" else "0"
    while i < len(code_RLE):
        freq = int(code_RLE[i:i + second_bit_length], 2)
        suites_bin += curr * freq
        curr = str(int(not int(curr)))
        i += second_bit_length
    print(len(suites_bin))
    arr = [suites_bin[i:i + first_bit_length] for i in range(0, len(suites_bin), first_bit_length)]
    if type == "nbr":
        return [int(arr[i],2) for i in range(len(arr))]
    else:
        return [chr(int(arr[i],2)) for i in range(len(arr))]
    
def decoder_RLE_v1(code_RLE,type,coding_bit_length):
    suites_symboles=''
    #case of 0 1 ...
    if type=="bin":
        i=1
        if code_RLE[0]=="0":
            curr="1"
        else:
            curr="0"
        while i< len(code_RLE):
            suites_symboles+=curr*int(code_RLE[i])
            curr=str(int(not int(curr)))
            i+=1
    # case of characters
    else:
        i=0
        while i< len(code_RLE):
            if code_RLE[i].isalpha():
                suites_symboles+=code_RLE[i].lower()
            else :
                suites_symboles+=int(code_RLE[i])*code_RLE[i+1].lower()
                i+=1
            i+=1
    return suites_symboles

def decoder_RLE_horiz(compressed_img,img_shape,first_bit_length,second_bit_length):
    decoded_sequence=decoder_RLE(compressed_img,"nbr",first_bit_length,second_bit_length)
    decoded_img=np.array(list(decoded_sequence)).reshape(img_shape).astype(int)
    return decoded_img

def decoder_RLE_vert(compressed_img,img_shape,first_bit_length,second_bit_length):
    decoded_sequence=decoder_RLE(compressed_img,"nbr",first_bit_length,second_bit_length)
    decoded_img=np.array(list(decoded_sequence)).reshape(img_shape, order='F').astype(int)
    return decoded_img


def decoder_RLE_zigzag(compressed_img, img_shape, first_bit_length, second_bit_length):
    decoded_arr = decoder_RLE(compressed_img, "nbr", first_bit_length, second_bit_length)
    decoded_arr = np.array(decoded_arr)
    
    rows, cols = img_shape[:2]  # Extract height & width
    channels = img_shape[2] if len(img_shape) == 3 else 1  # Check if RGB or Grayscale
    expected_size = rows * cols * channels
    print(f"Decoded array size: {decoded_arr.size}")
    print(f"Expected size : {expected_size}")

    if decoded_arr.size != expected_size:
        raise ValueError("Decoded data size mismatch. Check encoding/decoding process.")

    # Reshape based on channel order (not interleaved)
    decoded_arr = decoded_arr.reshape((channels, rows * cols))

    # Prepare output array
    table = np.zeros((rows, cols, channels), dtype=int) if channels > 1 else np.zeros((rows, cols), dtype=int)

    # Decode each channel separately
    for c in range(channels):
        if channels == 1:
             table=decode_zigzag(decoded_arr, rows, cols)
        else:
            table[:, :, c] = decode_zigzag(decoded_arr[c], rows, cols)
    return table

def decode_zigzag(decoded_arr, rows, cols):
    decoded_arr=decoded_arr.flatten()
    """Helper function to apply zigzag decoding for one channel."""
    nbr_diags = (rows + cols - 1)
    start = max(rows, cols) - 1
    end = -min(rows, cols)
    nbr_shifted_diags = min(rows, cols) - 1
    nbr_main_diags = nbr_diags - (nbr_shifted_diags * 2)
    fill_size = 0
    flip = True
    table = np.zeros((rows, cols), dtype=int)

    for i in range(start, end, -1):
        if i >= start - nbr_shifted_diags:
            fill_size += 1
        elif i < 0:
            fill_size -= 1
        tempo = np.zeros((rows, cols), dtype=int)
        popped = decoded_arr[:fill_size].copy()
        if flip:
            popped = np.flip(popped)
        flip = not flip
        decoded_arr = decoded_arr[fill_size:]
        eye_mask = np.eye(rows, cols, k=i, dtype=bool)
        tempo[eye_mask] = popped
        tempo = np.fliplr(tempo)
        table += tempo
    return table
def decode_any_image(compressed_img,metadata):
    if metadata['type']=='RGB':
        shape=(metadata['shape'][0],metadata['shape'][1],3)
    else:
        shape=(metadata['shape'][0],metadata['shape'][1])
    if metadata['coding_mode']=='zigzag':
        return decoder_RLE_zigzag(compressed_img,shape,metadata['first_bit'],metadata['second_bit'])
    elif metadata['coding_mode']=='vertical':
        return decoder_RLE_vert(compressed_img,shape,metadata['first_bit'],metadata['second_bit'])
    elif metadata['coding_mode']=='horizontal':
        return decoder_RLE_horiz(compressed_img,shape,metadata['first_bit'],metadata['second_bit'])
    else:
        raise ValueError("Invalid coding mode. Use 'zigzag', 'vertical', or 'horizontal'.")
def write_encoded_data(file_path, header, encoded_data):
    # Ensure header values are properly formatted to 8-bit
    formatted_header = formatted_header = [
        ord(header[0]),  # First byte of header
        (header[1] >> 8) & 0xFF,  # High byte of img shape 1
        header[1] & 0xFF,         # Low byte of img shape 1
        (header[2] >> 8) & 0xFF,  # High byte of img shape 2
        header[2] & 0xFF,         # Low byte of img shape 2
        ord(header[3]),           # Fourth byte of header
        header[4] & 0xFF,         # Fifth byte of header
        header[5] & 0xFF          # Sixth byte of header
    ]
    with open(file_path, 'wb') as f:
        f.write(bytes(formatted_header))  # Write header as bytes
        
        # Convert binary string into raw bits and write
        byte_array = bytearray()
        for i in range(0, len(encoded_data), 8):
            byte_chunk = encoded_data[i:i+8]
            byte_array.append(int(byte_chunk.ljust(8, '0'), 2))  # Pad last byte if needed
        
        f.write(byte_array)

def read_metadata(file_path):
    with open(file_path, 'rb') as f:
        header = list(f.read(8))  # Read first 6 bytes as header
        compressd_data = f.read()  # Read remaining bytes as compress_data

    # Reconstruct the second and third values (shape) from 2 bytes each
    shape_1 = (header[1] << 8) | header[2]  # Combine high and low bytes for the first shape value
    shape_2 = (header[3] << 8) | header[4]  # Combine high and low bytes for the second shape value
    # Convert the compress_data to binary form
    binary_data = ''.join(format(byte, '08b') for byte in compressd_data)
    
    image_type = 'RGB' if header[0] == ord('r') else 'Grayscale'
    shape = (shape_1, shape_2, 3) if image_type == 'RGB' else (shape_1, shape_2)
    coding_mode = {'z': 'zigzag', 'v': 'vertical', 'h': 'horizontal'}.get(chr(header[5]), 'unknown')
    first_bit = header[6]
    second_bit = header[7]
    metadata = {
        'type': image_type,
        'shape': shape,
        'coding_mode': coding_mode,
        'first_bit': first_bit,
        'second_bit': second_bit
    }
    
    return metadata,binary_data

# def decoder_RLE_zigzag(compressed_img,img_shape,first_bit_length,second_bit_length):
#     decoded_sequence=decoder_RLE(compressed_img,"nbr",first_bit_length,second_bit_length)
#     decoded_arr=np.array(list(decoded_sequence))
#     if len(img_shape)==2:
#         rows, cols= img_shape
#     else:
#         rows,cols,dim=img_shape
#     nbr_diags=(rows+cols-1)
#     start=max(rows,cols)-1
#     end=-min(rows,cols)
#     nbr_shifted_diags=min(rows,cols)-1
#     nbr_main_diags=nbr_diags-(nbr_shifted_diags*2)
#     fill_size=0
#     flip=True
#     table = np.zeros((rows, cols), dtype=int)
#     for i in range (start,end,-1):
#         if i >=start-nbr_shifted_diags:
#             fill_size+=1
#         elif i<0:
#             fill_size-=1
#         tempo= np.zeros((rows, cols), dtype=int)
#         popped=decoded_arr[:fill_size].copy()
#         if flip:
#             popped=np.flip(popped)
#         flip= not flip
#         decoded_arr=decoded_arr[fill_size:]
#         eye_mask = np.eye(rows, cols, k=i, dtype=bool)
#         tempo[eye_mask] = popped
#         tempo=np.fliplr(tempo)
#         table+=tempo
#     return table
      
class node:
    def __init__(self, char,freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
def huffman_tree(data):
    freq_table=Counter(data)
    nodes=[node(char,freq) for char,freq in freq_table.items()]
    while len(nodes)>1:
        nodes=sorted(nodes,key=lambda x:x.freq)
        left=nodes.pop(0)
        right=nodes.pop(0)
        addup=node(None,right.freq+left.freq)
        addup.left=left 
        addup.right=right
        nodes.append(addup)
    return nodes[0]
def huffman_dict(head,bit,dict):
    node=head
    if node is not None:
        if(node.char):
            dict[node.char]=bit
        else:
            huffman_dict(head.left,bit+'0',dict)
            huffman_dict(head.right,bit+'1',dict)
        return dict
def huffman_code(word):
    dict={}
    head=huffman_tree(word)
    dict=huffman_dict(head,'',dict)
    code=''
    for char in word:
        code+=dict[char]
    return code,dict
def huffman_decode(code,dict):
    word=''
    sequence=''
    for bit in code:
        sequence+=bit
        if sequence in dict.values():
            word+=list(dict.keys())[list(dict.values()).index(sequence)]
            sequence=''
    return word
      
def dict_LZ78(suites_symboles):
    dict=[]
    while suites_symboles:
        current=suites_symboles[0]
        j = 1
        while j<=len(suites_symboles):
            for index,sublist in enumerate(dict):
                if current == sublist[1]:
                    if j==len(suites_symboles):
                        dict.append([index,suites_symboles[j-1]])
                        suites_symboles=suites_symboles[j:]
                        break
                    current+=suites_symboles[j]
                    j+=1
                    break
            else:
                    # If prefix not found, add new entry
                prefix_index = 0
                if len(current) > 1:
                    # If current has a prefix, find its index
                    for index, sublist in enumerate(dict,1):
                        if sublist[1] == current[:-1]:
                            prefix_index = index
                            break
                    dict.append([prefix_index, current[-1]])
                else:
                    # Single character case
                    dict.append([0, current])

                # Remove the processed part from the string
                suites_symboles = suites_symboles[len(current):]
                break
    return dict
def decode_LZ78(dict):
    decoded_string=''
    for sublist in dict:
        if sublist[0]==0:
            decoded_string+=sublist[1]
        else:
            decoded_string+=dict[sublist[0]-1][1]+sublist[1]
    return decoded_string
def code_LZW(suites_symboles):
    # Initialize the dictionary with single-character mappings
    dictionary = {chr(i): i for i in range(256)}
    current = ""
    codes = []
    indice = 256

    for symbol in suites_symboles:
        combined = current + symbol
        if combined in dictionary:
            print("Combined:", combined, "is in the dictionary")
            current = combined
        else:
            codes.append(dictionary[current])
            dictionary[combined] = indice
            indice += 1
            current = symbol

    # Output the code for the last sequence
    if current:
        codes.append(dictionary[current])

    return codes

def save_huffman_to_bin(encoded_str, huff_dict, filename="huffman.bin"):
    # Convert encoded bitstring to bytes
    padded_encoded_str = encoded_str + '0' * ((8 - len(encoded_str) % 8) % 8)  # Padding to make it a multiple of 8
    byte_array = bytearray(int(padded_encoded_str[i:i+8], 2) for i in range(0, len(padded_encoded_str), 8))

    # Store both dictionary and encoded data
    with open(filename, "wb") as f:
        pickle.dump((byte_array, len(encoded_str), huff_dict), f)  # Save actual bit length to remove padding later

def load_huffman_from_bin(filename="huffman.bin"):
    with open(filename, "rb") as f:
        byte_array, bit_length, huff_dict = pickle.load(f)
    
    # Convert bytes back to bitstring
    bitstring = ''.join(f"{byte:08b}" for byte in byte_array)
    bitstring = bitstring[:bit_length]  # Remove padding

    # Decode using Huffman dictionary
    return huffman_decode(bitstring, huff_dict)

    
