import urllib2
import sys
import re

pages = range(248)

for p in pages[]:
#    print >> sys.stderr, "Downloading mashup list # %d ..." % p,
    listPage = urllib2.urlopen("http://www.programmableweb.com/category/all/mashups?page=%d&order=created&sort=desc" % p).read()

    pattern = re.compile("<a href=\"(\/mashup\/.+)\">")
    mashupPages = pattern.findall(listPage)
    
    for mp in mashupPages:
        print >> sys.stderr, "(%d) Downloading mashup %s ..." % (p, mp),

        try:
            mashupPage = urllib2.urlopen("http://www.programmableweb.com%s" % mp).read()

            with open ("mydata%s" % mp, 'wb') as f:
                f.write(mashupPage)
                f.close()
            print "done"
        except:
            print "FAILED"
