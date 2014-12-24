﻿import sys
import binascii
from PIL import Image

nb = 4  # число столбцов(32-х битных слов), составляющих State
nr = 10 # число раундов, которое является функцией Nk и Nb 
nk = 4  # число 32-х битных слов, составляющих шифроключ
	
def vigenere(data, key, func):
    key_len = len(key)
    output = []
    for i in range(len(data)):
        tmp = chr(func(ord(data[i]), ord(key[i % key_len])) % 256)
        output.append(tmp)
    return output
	

# XOR ключа раунда с формой	
def addRoundKey(state, RoundKeys, rnd):
    for i in range(4):
        for j in range(4):
            state[i][j] ^= RoundKeys[i][j+rnd*4]
    return state


def invSubBytes(state):
    for i in range(4):
        for j in range(4):
            state[i][j] = InvSbox[state[i][j]]
    return state


def invShiftRows(state):
    for i in range(4):
        state[i] = state[i][-i:] + state[i][:-i]
    return state


# Умножение в поле Галуа	
def GMul(a, b): 
    p = 0
    for counter in range(8):
        if b & 1:
            p ^= a
        hi_bit_set = a & 0x80
        a <<= 1
        a &= 0xff
        if hi_bit_set:
            a ^= 0x1b
        b >>= 1;
    return p


def InvMixColumns(state):				
    tmp = [0] * 4
    for s in range(4):
        tmp[s] = [0] * 4
    for i in range(4):
        tmp[0][i] = GMul(0x0e, state[0][i]) ^ GMul(0x0b, state[1][i]) ^ GMul(0x0d, state[2][i]) ^ GMul(0x09, state[3][i])
        tmp[1][i] = GMul(0x09, state[0][i]) ^ GMul(0x0e, state[1][i]) ^ GMul(0x0b, state[2][i]) ^ GMul(0x0d, state[3][i])
        tmp[2][i] = GMul(0x0d, state[0][i]) ^ GMul(0x09, state[1][i]) ^ GMul(0x0e, state[2][i]) ^ GMul(0x0b, state[3][i])
        tmp[3][i] = GMul(0x0b, state[0][i]) ^ GMul(0x0d, state[1][i]) ^ GMul(0x09, state[2][i]) ^ GMul(0x0e, state[3][i])
    return tmp


def Xor(state,tmp, n):
    for i in range(n):
        state[i] = state[i] ^ tmp[i]
    return state


# получение ключей для всех раундов	
def KeyExpansion(key_symbols):
    key = bytearray(key_symbols)
    if len(key) < 4 * nk:
        for i in range(4 * nk - len(key)):
            key.append(0x01)
    key_schedule = [[] for i in range(4)]
    for r in range(4):
        for c in range(nk):
            key_schedule[r].append(key[r + 4 * c])
    for col in range(nk, nb * (nr + 1)):
        if col % nk == 0:
            tmp = [key_schedule[row][col - 1] for row in range(1, 4)]
            tmp.append(key_schedule[0][col - 1])

            for j in range(len(tmp)):
                sbox_row = tmp[j] // 0x10
                sbox_col = tmp[j] % 0x10
                sbox_elem = Sbox[16 * sbox_row + sbox_col]
                tmp[j] = sbox_elem

            for row in range(4):
                s = (key_schedule[row][col - 4]) ^ (tmp[row]) ^ (Rcon[row][int(col / nk - 1)])
                key_schedule[row].append(s)

        else:
            for row in range(4):
                s = key_schedule[row][col - 4] ^ key_schedule[row][col - 1]
                key_schedule[row].append(s)
    return key_schedule


def decrypt(input_bytes, key):
    input_bytes = bytearray(input_bytes)
    state = []
    for i in range(4):
        state.append(input_bytes[i::nb])

    key_schedule = KeyExpansion(key)
    state = addRoundKey(state, key_schedule, 10)

    for rnd in reversed(range(1, nr)):
        state = invShiftRows(state)
        state = invSubBytes(state)
        state = addRoundKey(state, key_schedule, rnd )
        state = InvMixColumns(state)

    state = invShiftRows(state)
    state = invSubBytes(state)
    state = addRoundKey(state, key_schedule, 0)

    result = []
    for i in range(nb):
        for j in range(4):
            result.append(state[j][i])
    result = [chr(x) for x in result]
    return result
	
	
Sbox = [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76, 
	0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0, 
	0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15, 
	0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75, 
	0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84, 
	0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf, 
	0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8, 
	0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, 
	0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73, 
	0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb, 
	0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79, 
	0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08, 
	0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a, 
	0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e, 
	0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf, 
	0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16]
	

InvSbox = [0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
	0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
	0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
	0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
	0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
	0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
	0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
	0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
	0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
	0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
	0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
	0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
	0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
	0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
	0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
	0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d]		
	
	
Rcon = [
	[0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36],
	[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
	[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
	[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]]


def rgb2hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)
	
	
def bin2str(binary):
    message = binascii.unhexlify('%x' % (int('0b'+binary,2)))
    return message
	
	
def decode(hexcode):
    if hexcode[-1] in ('0', '1'):
        return hexcode[-1]
    else:
        return None

		
def Extracting(fname):
    img = Image.open(fname)
    mode = img.mode
    binary = ''
    if mode in ('RGBA'):
        img.convert('RGBA')
        data = img.getdata()
        for item in data:
            digit = decode(rgb2hex(item[0],item[1],item[2]))
            if digit == None:
                pass
            else:
                binary = binary + digit
                if(binary[-16:] == '1111111111111110'):
                    return bin2str(binary[:-16])
        return bin2str(binary)
    return  None        

		
def main(key_vig, key_aes, imageFile):
    res = ''		
    res = Extracting(imageFile)
    print('LSB - - - > ok')
    decrypted_data = []
    temp = []
    for byte in res:
        temp.append(byte)
        if len(temp) == 16:
            decrypted_part = decrypt(temp, key_aes)
            decrypted_data.extend(decrypted_part)
            del temp[:]
			
    decrypted_data = decrypted_data[:-1]
    count = decrypted_data.count('\x00')
	
    [decrypted_data.remove('\x00') for i in range(count)]

    print('AES - - - > ok')			
    cd = 'd'		
    do = {'c': lambda x, y: x + y, 'd': lambda x, y: x - y}
    text = vigenere(decrypted_data, key_vig, do[cd])
	
    print('Vigener - - - > ok') 
    return text	
   
if __name__ == '__main__':
    main()