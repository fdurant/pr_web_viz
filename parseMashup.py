import glob
import re
import csv
import sys

filelist = glob.glob("mydata/mashup/*")

csvwriter = csv.writer(sys.stdout, delimiter=',')

header = []
header.append('mashupIdNumeric')
header.append('mashupIdString')
header.append('mashupName')
header.append('relatedApiStringIds')
header.append('mashupTags')
header.append('mashupUrl')
#header.append('')
csvwriter.writerow(header)

def getNumericId(mashupPage):
    pattern = re.compile("<link rel=\"shortlink\" href=\"http:\/\/www.programmableweb.com\/node\/(\d+)\"")
    nid = re.search(pattern,mashupPage).group(1)
#    print >> sys.stderr, "nid = %s" % nid
    return nid

def getStringId(mashupPage):
    pattern = re.compile("<link rel=\"canonical\" href=\"http:\/\/www.programmableweb.com\/mashup\/(.+)\"")
    sid = re.search(pattern,mashupPage).group(1)
#    print >> sys.stderr, "sid = %s" % sid
    return sid

def getName(mashupPage):
    pattern = re.compile("property=\"og:title\"\s+content=\"(.+)\"")
    name = re.search(pattern,mashupPage).group(1)
#    print >> sys.stderr, "name = %s" % name
    return name

def getApiStringIds(mashupPage):
    try:
        patternString = "<div class=\"field\">\s+<label>Related APIs</label>\s+<span>(.*?)</span>"
        pattern = re.compile(patternString, re.MULTILINE)
        tmp = re.search(pattern,mashupPage).group(1)
        apiStringIds = re.findall("href=\"/api/(.*?)\"", tmp)
    except AttributeError:
        apiStringIds = []
    return "|".join(apiStringIds)

def getTags(mashupPage):
    try:
        patternString = "<div class=\"field\">\s+<label>Tags</label>\s+<span>(.*?)</span>"
        pattern = re.compile(patternString, re.MULTILINE)
        tmp = re.search(pattern,mashupPage).group(1)
        tags = re.findall("<a href=\"/category/.*?\">(.*?)</a>", tmp)
    except AttributeError:
        tags = []
    return "|".join(tags)

def getUrl(mashupPage):
    try:
        patternString = "<div class=\"field\">\s+<label>URL</label>\s+<span><a[^>]*?>(.*?)</a></span>"
        pattern = re.compile(patternString, re.MULTILINE)
        url = re.search(pattern,mashupPage).group(1)
    except AttributeError:
        url = ""
    return url

for i,f in enumerate(filelist):
    if i % 100 == 0:
        print >> sys.stderr, "Processing mashup file %d/%d ..." % (i, len(filelist)),

    with open(f, 'r') as mashupFile:
        mashupPage = mashupFile.read()
    mashupFile.close()

    row = []

    row.append(getNumericId(mashupPage))
    row.append(getStringId(mashupPage))
    row.append(getName(mashupPage))
    row.append(getApiStringIds(mashupPage))
    row.append(getTags(mashupPage))
    row.append(getUrl(mashupPage))

    csvwriter.writerow(row)

    if i % 100 == 0:
        print >> sys.stderr, "done"
