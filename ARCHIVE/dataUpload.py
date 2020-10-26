#Test script to upload documents
import socket

#Function to test internet connectivity by device
#This snippet is taken from: https://medium.com/better-programming/how-to-check-the-users-internet-connection-in-python-224e32d870c8
def testConnect(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False

def dbUpload():
    

if __name__ == '__main__':
    testConnect()
