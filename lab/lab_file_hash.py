from hashlib import file_digest, algorithms_available
from sys import argv
from glob import glob
from os.path import isfile

# available: ['blake2b', 'blake2s', 'md5', 'md5-sha1', 'ripemd160',
# 'sha1', 'sha224', 'sha256', 'sha384', 'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512', 'sha512', 'sha512_224', 'sha512_256', 'shake_128', 'shake_256', 'sm3']
for x in argv[1:]:
    for fp in glob(x):
        if isfile(fp):
            with open(fp, 'rb') as fh:
                digest = file_digest(fh, 'sha1')
                print(digest.hexdigest())

print('available:', sorted(algorithms_available))
