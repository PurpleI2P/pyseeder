class RouterInfo:
    
    def __init__(self, filename):
        self.yggdrasil = False
        with open(filename, 'rb') as f:
            buf = f.read()
            if len(buf) < 387:
                return 
            offset = 384 # crypto and signing keys
            offset += int.from_bytes(buf[offset + 1: offset + 3], byteorder='big') # size from certificate 
            offset += 3 # certificate
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
            style = self.readstring(buf[offset:]) # transport style
            offset += len(style) + 1 # style string
            size = int.from_bytes(buf[offset:offset+2], byteorder='big') # size of properties
            offset += 2
            if not self.yggdrasil and style == 'NTCP2': # possible yggdrasil?
                r = offset
                while r < size + offset:
                    key = self.readstring(buf[r:])
                    r += len(key) + 2 # length and =
                    if key == 'host':
                        value = self.readstring(buf[r:])
                        firstcolon = value.find(':')
                        if firstcolon > 0: # ipv6 address
                            first = int(value[0:firstcolon], 16) # first segment of ipv6 address
                            if first >= 0x0200 and first <= 0x03FF: # yggdrasil range
                                self.yggdrasil = True
                        break
                    r += len(self.readstring(buf[r:])) + 2 # length and ;               
            offset += size
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

    def isyggdrasil(self):
        return self.yggdrasil

