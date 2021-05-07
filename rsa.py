import secrets
import math


def is_prime(n, iterations=100):
    for i in range(iterations):
        a = secrets.randbelow(n-4) + 2
        if pow(a, n-1, n) != 1:
            return False
    return True # probably

def random_number(bits):
    n = 0
    while not n & (3 << bits-2) == (3 << bits-2):
        n = secrets.randbits(bits)
    return n

def random_prime(bits):
    n = random_number(bits)
    while not is_prime(n):
        n = random_number(bits)
    return n

def RSA_key(bits):
    p = random_prime(bits//2)
    q = random_prime(bits//2)
    n = p * q
    return n


if __name__ == '__main__':
    bits = 1024
    n = RSA_key(bits)
    print(f"{bits}-bit RSA key: {n}")