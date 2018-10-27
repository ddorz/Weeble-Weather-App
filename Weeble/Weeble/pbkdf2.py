import hmac
import hashlib
from struct import Struct
from operator import xor
from itertools import izip, starmap

_pack_int = Struct('>I').pack


def pbkdf2(data, salt, iterations=1000, keylen=24, hashf=None):
    hashf = hashf or hashlib.sha1
    mac = hmac.new(data, None, hashf)

    def _urandom(x, m=mac):
        h = m.copy()
        h.update(x)
        return map(ord, h.digest())

    buf = []
    for block in range(1, -(-keylen // mac.digest_size) + 1):
        rv = u = _urandom(salt + _pack_int(block))
        for i in range(iterations - 1):
            u = _urandom(''.join(map(chr, u)))
            rv = starmap(xor, izip(rv, u))
        buf.extend(rv)

    return (''.join(map(chr, buf))[:keylen]).encode('hex')