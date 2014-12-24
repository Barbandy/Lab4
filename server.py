import socket
import argparse
import decrypt


def readFile(fname):
    try:
        with open(fname, 'rb') as f:
            inf = f.read()
    except IOError:
        exit('No such file or directory ' + fname)
    return inf	
	
	
def writeFile(inf):
    try:
        with open("result.txt", 'wb') as f:
		    f.write(''.join(inf))
    except IOError:
        exit('No such file or directory ' + fname)

		
def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('keyVig', help = "file with key for Vizhiner cipher", default = 'keyVig')
    parser.add_argument('keyAes', help = "file with key for AES cipher", default = 'keyAes')
    parser.add_argument('port', help = "for example '9013'")
    return parser.parse_args()	
		
		
def get(port):
    sock = socket.socket()
    sock.bind(('', int(port)))
    sock.listen(1)
    print('Listen port', port)
    try:
        sock.settimeout(60)
        conn, addr = sock.accept()
        sock.settimeout(None)
    except socket.timeout:
        exit('Connection timed out')
    except socket.error:
        exit('Error of connection')
    print('Connected:', addr, '. Receipt of messages')
    data = bytes()
    tmp = conn.recv(1024)
    while tmp:
        data += tmp
        tmp = conn.recv(1024)

    print('Message received! (', len(data), 'bytes)')
    conn.close()
    sock.close()
    return data
        
	
	
def main():
    args = getArgs()
    keyVig = readFile(args.keyVig)
    keyAes = readFile(args.keyAes)
    img = get(args.port)
    with open("test.png", 'wb') as f:
        f.write(bytearray(img))
    res = decrypt.main(keyVig, keyAes, 'test.png')
    writeFile(res)
    print('tne end')


if __name__ == '__main__':
    main()