import sys
import signal
import threading
import requests
import dnslib
import dnslib.server
import kyotocabinet

class BlockingCloudFlareResolver(dnslib.server.BaseResolver):
    def __init__(self, gravity_file):
        self.gravity = kyotocabinet.DB()
        self.gravity.open(gravity_file, kyotocabinet.DB.OREADER)
        super(type(self))

    def resolve(self, request, handler):
        if any([self.gravity.check(q.qname) != -1 for q in request.questions]):
            reply = request.reply()
            reply.header.rcode = dnslib.RCODE.REFUSED
            return reply

        try:
            response = requests.post('https://1.1.1.1/dns-query',
                    headers={'Content-Type': 'application/dns-udpwireformat'},
                    data=request.pack())
            reply = dnslib.DNSRecord.parse(response.content)
        except:
            reply = request.reply()
            reply.header.rcode = dnslib.RCODE.SERVFAIL
        finally:
            return reply

def shutdown_server(signum, frame):
    threading.Thread(target=lambda: server.stop()).start()
    server.server.resolver.gravity.close()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_server)
server = dnslib.server.DNSServer(BlockingCloudFlareResolver('gravity.kch'))
server.start()
