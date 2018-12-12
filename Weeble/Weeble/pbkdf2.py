import hmac
import hashlib
from struct import Struct
from operator import xor
from itertools import starmap
try:
    from itertools import izip as zip
except ImportError:
    pass
import binascii

_pack_int = Struct('>I').pack


# pbkdf2 key stretching function -- One-way encryption for user passwords to be stored in db
def pbkdf2(data, salt, iterations=1000, keylen=24, hashf=None):
    hashf = hashf or hashlib.sha1
    mac = hmac.new(bytes(data, 'latin-1'), None, hashf)

    def _urandom(x, m=mac):
        h = m.copy()
        h.update(x.encode('utf-8'))
        return bytearray(h.digest())

    buf = []
    for block in range(1, -(-keylen // mac.digest_size) + 1):
        rv = u = _urandom(salt + ''.join(map(chr, _pack_int(block))))
        for i in range(iterations - 1):
            u = _urandom(''.join(map(chr, u)))
            rv = starmap(xor, zip(rv, u))
        buf.extend(rv)

    return binascii.hexlify((''.join(map(chr, buf))[:keylen]).encode(encoding='utf-8'))