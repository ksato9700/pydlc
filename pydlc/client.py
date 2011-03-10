#
# Copyright 2011 Kenichi Sato <ksato9700@gmail.com>
#
import os
import urlparse
import datetime

import pycurl
import dns.resolver


class Client(object):

    def progress(self, download_t, download_d, upload_t, upload_d):
        ts = (datetime.datetime.utcnow(), download_d)
        self.tslist.append(ts)

    def __init__(self, url):
        self.urlobj = urlparse.urlparse(url)
        self.addresses = map(lambda rdata: getattr(rdata, 'address'), 
                             dns.resolver.query(self.urlobj.hostname, 'A'))
        self.c = pycurl.Curl()
        self.c.setopt(pycurl.NOPROGRESS, 0)
        self.c.setopt(pycurl.PROGRESSFUNCTION, self.progress)
        self.c.setopt(pycurl.HTTPHEADER, ["Host:"+self.urlobj.hostname])
        #self.c.setopt(pycurl.VERBOSE, 1)
        self.c.setopt(pycurl.WRITEDATA, open(os.devnull,"w"))

    def download(self):
        for address in self.addresses:
            netloc = address + (":" + self.urlobj.port if self.urlobj.port else "")
            newurl = urlparse.urlunparse(self.urlobj[:1] + (netloc,) + self.urlobj[2:])
            
            self.c.setopt(pycurl.URL, newurl)
            self.tslist = []
            self.c.perform()

            print "Average speed: %0.2f Mbps" % (self.c.getinfo(pycurl.SPEED_DOWNLOAD)*8/1024.0/1024.0)

            #print self.c.getinfo(pycurl.NAMELOOKUP_TIME)
            #print self.c.getinfo(pycurl.CONNECT_TIME)
            #print self.c.getinfo(pycurl.APPCONNECT_TIME)
            #print self.c.getinfo(pycurl.PRETRANSFER_TIME)
            #print self.c.getinfo(pycurl.STARTTRANSFER_TIME)
            #print self.c.getinfo(pycurl.REDIRECT_TIME)
            print "Total time: %0.2f sec" % self.c.getinfo(pycurl.TOTAL_TIME)

            llen = len(self.tslist)
            step =  llen/10
            
            #for i in range(llen-15, llen):
            #    print self.tslist[i]

            try :
                for i in range (0, llen, step):
                    tdelta = self.tslist[i+step][0] - self.tslist[i][0]
                    ddelta = self.tslist[i+step][1] - self.tslist[i][1]
                    tpos = self.tslist[i+step][0] - self.tslist[0][0] + tdelta/2
                    print "%0.2f Mbps @ %0.2f" % (ddelta*8/tdelta.total_seconds()/1024.0/1024.0, tpos.total_seconds())

            except IndexError:
                pass

            #break

def main():
    import sys
    client = Client(sys.argv[1])
    client.download()

if __name__ == '__main__':
    main()
