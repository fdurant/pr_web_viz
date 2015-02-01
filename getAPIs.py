import urllib2
import sys
import re

pages = range(115)

for p in pages[1:]:
#    print >> sys.stderr, "Downloading API list # %d ..." % p,
    listPage = urllib2.urlopen("http://www.programmableweb.com/apis/directory?page=%d" % p).read()
#    print page

    pattern = re.compile("<a href=\"(\/api\/.+)\">")
    apiPages = pattern.findall(listPage)    

    for ap in apiPages:
        print >> sys.stderr, "(%d) Downloading api %s ..." % (p, ap),

        try:
            apiPage = urllib2.urlopen("http://www.programmableweb.com%s" % ap).read()

            with open ("mydata%s" % ap, 'wb') as f:
                f.write(apiPage)
                f.close()
            print "done"
        except:
            print "FAILED"
