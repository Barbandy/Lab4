import socket
import argparse
import encrypt



def readFile(fname):
    try:
        with open(fname, 'rb') as f:
            inf = f.read()
    except IOError:
        exit('No such file or directory ' + fname)
    return inf	


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('inFile', help = "name of file with data", default = 'indata')
    parser.add_argument('keyVig', help = "file with key for Vizhiner cipher", default = 'keyVig')
    parser.add_argument('keyAes', help = "file with key for AES cipher", default = 'keyAes')
    parser.add_argument('imageFile', help = "name of image file", default = 'test.png')
    parser.add_argument('host', help = "for example 'localhost'")
    parser.add_argument('port', help = "for example '9013'")
    return parser.parse_args()	
	
	
def send(data, host, port):
    sock = socket.socket()
    try:
        sock.connect((host, int(port)))
        print('Connection with ' + host)
    except socket.error:
        exit('Error connection with ' + host)
    sock.send(data)
    print('Message sent! (', len(data), ' bytes)')
    sock.close()


def main():
    args = getArgs()
    data = readFile(args.inFile)
    keyVig = readFile(args.keyVig)
    keyAes = readFile(args.keyAes)
    res = encrypt.main(data, keyVig, keyAes, args.imageFile)
    send(res, args.host, args.port)
    print('tne end')
	
if __name__ == '__main__':
    main()	
	
	
