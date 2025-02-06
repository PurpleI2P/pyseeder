class RouterInfo:
    
    def __init__(self, filename):
        with open(filename, 'rb') as f:
            buf = f.read()
            if len(buf) < 391: # TODO: parse identity
                return 
            offset = 391
            self.timestamp = int.from_bytes(buf[offset: offset + 8], byteorder='big') # 8 bytes timestamp
            offset += 8
            offset += self.readaddresses(buf[offset:]) # addresses
            offset += buf[offset]*32 + 1; # peers  
            self.properties = {}
            offset += self.readproperties(buf[offset:]) # properties

    def readaddresses(self, buf):
        numaddresses = buf[0]
        offset = 1
        for i in range(0, numaddresses):
            offset += 1 # cost
            offset += 8 # date
            offset += len(self.readstring(buf[offset:])) + 1 # style string
            size = int.from_bytes(buf[offset:offset+2], byteorder='big') # properties
            offset += size + 2
        return offset
    
    def readproperties(self, buf):
        size = int.from_bytes(buf[0:2], byteorder='big')
        r = 2
        while r < size + 2:
            key = self.readstring(buf[r:])
            r += len(key) + 2 # length and =
            value = self.readstring(buf[r:])
            r += len(value) + 2 # length and ;
            self.properties[key] = value
        return size

    def readstring(self, buf):
        l = buf[0]
        return buf[1:l+1].decode('utf-8')

    def getversion(self):
        if 'router.version' in self.properties:
            v = 0
            for c in self.properties['router.version']:
                if c >= '0' and c <= '9':
                    v *= 10
                    v += (ord(c) - ord('0'))
            return v
        else:
            return 0

    def hasinvalidcaps(self):
        invalidcaps = set('UDEG')
        return any((c in invalidcaps) for c in self.properties['caps'])

    def isvalid(self):
        return self.getversion() >= 959 and not self.hasinvalidcaps() # version >= 0.9.59 and no 'U', 'D', 'E' or 'G' caps

