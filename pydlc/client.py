#
# Copyright 2011 Kenichi Sato <ksato9700@gmail.com>
#
import urlparse
import urllib2
import httplib
import datetime

import dns.resolver


class NP_HTTPConnection(httplib.HTTPConnection):
    def getresponse(self):
        return super(NP_HTTPConnection, self).getresponse(buffering=False)

class NB_HTTPHandler(urllib2.HTTPHandler):
    def http_open(self, req):
        return self.do_open(NB_HTTPConnection, req)

BUFSIZ = 4096*1024

class Client(object):
    def __init__(self, url):
        self.urlobj = urlparse.urlparse(url)
        self.addresses = map(lambda rdata: getattr(rdata, 'address'), 
                             dns.resolver.query(self.urlobj.hostname, 'A'))

    def download(self):
        for address in self.addresses:
            netloc = address + (":" + self.urlobj.port if self.urlobj.port else "")
            newurl = urlparse.urlunparse(self.urlobj[:1] + (netloc,) + self.urlobj[2:])
            print newurl
            request = urllib2.Request(newurl, headers={'Host':self.urlobj.hostname})
            fp = urllib2.urlopen(request)
            tslist = []
            tslist.append((0, datetime.datetime.utcnow()))
            while(True):
                print '.'
                buf = fp.read(BUFSIZ)
                l = len(buf)
                tslist.append((l,datetime.datetime.utcnow()))
                if not l:
                    break

            for i in range(len(tslist)-1):
                print tslist[i+1][0] * 8 / (tslist[i+1][1] - tslist[i][1]).total_seconds() / 1000.0 / 1000.0 
            


def main():
    import sys
    client = Client(sys.argv[1])
    client.download()

if __name__ == '__main__':
    main()
