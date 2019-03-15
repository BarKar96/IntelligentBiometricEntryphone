import TCPClient
from random import randint

sharedPrime = 23  # p
sharedBase = 5  # g


RPiPrivateSecret = randint(1, 20)


print("Publicly Shared Variables:")
print("    Publicly Shared Prime: ", sharedPrime)
print("    Publicly Shared Base:  ", sharedBase)


def negotiateDHKeys():
    A = (sharedBase ** RPiPrivateSecret) % sharedPrime
    print("\nSending public Key: ", A)
    TCPClient.startTCPClient("DH;"+str(A))
    


def calculateSharedSecret(androidPublicKey):
    print("\n------------\n")
    sharedSecret = (int(androidPublicKey) ** RPiPrivateSecret) % sharedPrime
    print("Calculated shared key: " +str(sharedSecret))
    return sharedSecret
