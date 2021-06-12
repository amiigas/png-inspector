import os.path
import secrets

import myrsa
import rsa
from image import PNG_Image

image_path = '/Users/Aleksy/Desktop/images/tux-plte.png'
filepath = os.path.abspath(image_path)
filepath_encrypted = os.path.abspath(image_path.replace('.png', '-encrypted.png'))
filepath_decrypted = os.path.abspath(image_path.replace('.png', '-decrypted.png'))

bits = 1024
public, private = myrsa.generate_keys(bits)
# public, private = rsa.newkeys(bits)
iv = secrets.randbits(bits-1)
mode = 'CBC'

img = PNG_Image(filepath)
print("Encrypting...")
img.encrypt(public, bits, mode=mode, iv=iv)
img.save(filepath_encrypted)
print("Decrypting...")
img.decrypt(private, bits, mode=mode, iv=iv)
img.save(filepath_decrypted)
