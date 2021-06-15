import time
import myrsa
import rsa

class Timer:
    def __init__(self):
        self.start_time = 0

    def start(self):
        self.start_time = time.perf_counter()

    def stop(self, verbose=False):
        elapsed_time = time.perf_counter() - self.start_time
        self.start_time = 0
        if verbose:
            print(f"Elapsed time: {elapsed_time:0.6f} seconds")
        return elapsed_time

t = Timer()
bit_lengths = [128, 256, 512, 1024, 2048, 4096]
print("{:<10}{:10}{:10}".format("bits", "myrsa", "rsa"))

for bits in bit_lengths:
    t.start()
    public, private = myrsa.generate_keys(bits)
    t1 = t.stop()

    t.start()
    public, private = rsa.newkeys(bits)
    t2 = t.stop()

    print("{:<10}{:<10.6f}{:<10.6f}".format(bits, t1, t2))

"""
bits      myrsa     rsa       
128       0.006552  0.002179  
256       0.015569  0.003677  
512       0.128227  0.025998  
1024      0.447283  0.129258  
2048      8.464320  1.795961  
4096      98.011895 189.381891
"""