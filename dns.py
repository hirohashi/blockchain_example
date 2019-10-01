import random
import socket

class DNSFlags():
    def __init__(self, qr, opcode, aa, tc, rd, ra, z, ad, cd, rcode):
        self.qr = qr # 1bit
        self.opcode = opcode # 4bit
        self.aa = aa # 1bit
        self.tc = tc # 1bit
        self.rd = rd # 1bit
        self.ra = ra # 1bit
        self.z = z # 1bit
        self.ad = ad # 1bit
        self.cd = cd # 1bit
        self.rcode = rcode # 4bit
    
    def to_bytes(self):
        result = bytearray()
        result.append(
            self.qr << 7 | 
            (self.opcode >> 3 & 0x1) << 6 |
            (self.opcode >> 2 & 0x1) << 5 |
            (self.opcode >> 1 & 0x1) << 4 |
            (self.opcode >> 0 & 0x1) << 3 |
            self.aa << 2 |
            self.tc << 1 |
            self.rd << 0
        )
        result.append(
            self.ra << 7 |
            self.z << 6 |
            self.ad << 5 |
            self.cd << 4 |
            (self.rcode >> 3 & 0x1) << 3 |
            (self.rcode >> 2 & 0x1) << 2 |
            (self.rcode >> 1 & 0x1) << 1 |
            (self.rcode >> 0 & 0x1) << 0
        )
        return bytes(result)

class DNSHeader():
    def __init__(self, flags, qdcount, ancount, nscount, arcount):
        self.id = random.randint(0, 10000)
        self.flags = flags
        self.qdcount = qdcount
        self.ancount = ancount
        self.nscount = nscount
        self.arcount = arcount
    
    def to_bytes(self):
        result = bytearray()
        result.append(self.id >> 8 & 0xff)
        result.append(self.id & 0xff)
        for b in self.flags.to_bytes():
            result.append(b)
        result.append(self.qdcount >> 8 & 0xff)
        result.append(self.qdcount & 0xff)
        result.append(self.ancount >> 8 & 0xff)
        result.append(self.ancount & 0xff)
        result.append(self.nscount >> 8 & 0xff)
        result.append(self.nscount & 0xff)
        result.append(self.arcount >> 8 & 0xff)
        result.append(self.arcount & 0xff)
        return bytes(result)

class QuerySection():
    def __init__(self, domain, dtype, dclass):
        self.domains = domain.split(".")
        self.dtype = dtype
        self.dclass = dclass
    
    def to_bytes(self):
        result = bytearray()
        for domain in self.domains:
            result.append(len(domain))
            for b in bytes(domain.encode()):
                result.append(b)
        result.append(0) # 終端文字
        result.append((self.dtype >> 8) & 0xff)
        result.append(self.dtype & 0xff)
        result.append((self.dclass >> 8) & 0xff)
        result.append(self.dclass & 0xff)
        return bytes(result)

class DNS():
    def __init__(self, header, sections, ip="127.0.0.1", port=53):
        self.header = header
        self.sections = sections
        self.address = (ip, port)

    def to_bytes(self):
        result = bytearray()
        for b in self.header.to_bytes():
            result.append(b)
        for section in self.sections:
            for b in section.to_bytes():
                result.append(b)
        return bytes(result)

    @staticmethod
    def domain_to_ip(domain):
        # make packet
        flags = DNSFlags(
            qr = 0, # 問い合わせ=0, 応答=1
            opcode = 0, # 問い合わせ=0, notify=4, update=5
            aa = 0, # 管理権限の応答=1
            tc = 0, # 応答が切り詰められた=1
            rd = 1, # 名前解決するかどうか
            ra = 0, # 名前解決可能=1, 非サポート=0
            z = 0, # 予約（常に0)
            ad = 0, # 問い合わせの際に応答のadが理解できる=1, 応答の際DNSSECの検証が成功=1
            cd = 0, # 問い合わせの際，DNSSECの検証を無効=1
            rcode = 0 # 応答コード(NOERROR, SERVFAIL, NXDOMAIN, REFUSED)
        )
        header = DNSHeader(
            flags = flags,
            qdcount = 1, # 問い合わせセクション数
            ancount = 0, nscount = 0, arcount = 0
        )
        sections = []
        sections.append(QuerySection(
            domain = domain,
            dtype = 1, # A record = 0x0001
            dclass = 1, # IN = 0x0001
        ))
        dns = DNS(header, sections)

        # communicate
        BUFFER = 1024
        query = dns.to_bytes()
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # internet, udp
        client.sendto(query, dns.address)
        data, address = client.recvfrom(BUFFER)
        
        # get answer
        rcode = data[3] & 0xf
        if rcode == 0:
            answer = data[len(query)+12:len(query)+16]
            return "%d.%d.%d.%d" % (answer[0], answer[1], answer[2], answer[3])
        else:
            raise Exception('error code %d: cannot resolve domain. ' % rcode) 
    @staticmethod
    def ip_to_domain():
        pass
