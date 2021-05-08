import secrets


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

def euler(p, q):
    return (p-1) * (q-1)

def mod_mul_inv(a, m):
    return pow(a, -1, m)

def generate_keys(bits, e=65537):
    p = random_prime(bits//2)
    q = random_prime(bits//2)
    n = p * q
    phi = euler(p, q)
    d = mod_mul_inv(e, phi)
    return (e, n), (d, n)

def encode(message, public_key):
    e = public_key[0]
    n = public_key[1]
    c = pow(message, e, n)
    return c

def decode(ciphertext, private_key):
    d = private_key[0]
    n = private_key[1]
    m = pow(ciphertext, d, n)
    return m

if __name__ == '__main__':
    bits = 1024
    public, private = generate_keys(bits)

    plaintext = "poggers"
    padded = [ord(val) for val in plaintext]
    ciphertext = [encode(val, public) for val in padded]
    decoded = [decode(val, private) for val in ciphertext]
    decoded_plaintext = [chr(val) for val in decoded]

    print(f"plaintext: {plaintext}")
    print(f"padded: {padded}")
    print(f"ciphertext: {ciphertext}")
    print(f"decoded: {decoded}")
    print(f"decoded_plaintext: {decoded_plaintext}")
