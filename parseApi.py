import glob
import re
import csv
import sys

filelist = glob.glob("mydata/api/*")

csvwriter = csv.writer(sys.stdout, delimiter=',')

header = []
header.append('apiIdNumeric')
header.append('apiIdString')
header.append('apiName')
header.append('apiProvider')
header.append('apiEndpoint')
header.append('apiHomepage')
header.append('apiPrimaryCategory')
header.append('apiNrFollowers')
header.append('apiNrMashups')
header.append('APIForum')
#header.append('')
csvwriter.writerow(header)

def getNumericId(apiPage):
    pattern = re.compile("<link rel=\"shortlink\" href=\"http://www.programmableweb.com/node/(\d+)\"")
    nid = re.search(pattern,apiPage).group(1)
#    print >> sys.stderr, "nid = %s" % nid
    return nid

def getStringId(pathToFile):
    pattern = re.compile("^.+\/([^\/]+)$")
    sid = re.search(pattern,pathToFile).group(1)
#    print >> sys.stderr, "sid = %s" % sid
    return sid

def getName(apiPage):
    pattern = re.compile("property=\"og:title\"\s+content=\"(.+)\"")
    name = re.search(pattern,apiPage).group(1)
#    print >> sys.stderr, "name = %s" % name
    return name

def getSpecsField(apiPage,fieldName):
    try:
        patternString = "<div class=\"field\">\s+<label>%s</label>\s+<span><a[^>]*?>([^<]*)</a></span>" % fieldName
        pattern = re.compile(patternString, re.MULTILINE)
        field = re.search(pattern,apiPage).group(1)
    except AttributeError:
        try:
            patternString = "<div class=\"field\">\s+<label>%s</label>\s+<span>([^<]*)</span>" % fieldName
            pattern = re.compile(patternString, re.MULTILINE)
            field = re.search(pattern,apiPage).group(1)        
        except AttributeError:
            field = ""
    return field

def getNrFollowers(apiPage):
    try:
        pattern = re.compile("<span>Followers\s+\((\d+)\)<\/span>")
        nrFollowers = re.search(pattern,apiPage).group(1)
    except AttributeError:
        nrFollowers = 0
    return nrFollowers

def getNrMashups(apiPage):
    try:
        pattern = re.compile("<span>API Mashups\s+\((\d+)\)<\/span>")
        nrMashups = re.search(pattern,apiPage).group(1)
    except AttributeError:
        nrMashups = 0
    return nrMashups

for i,f in enumerate(filelist):
    if i % 100 == 0:
        print >> sys.stderr, "Processing API file %d/%d ..." % (i, len(filelist)),

    with open(f, 'rb') as apiFile:
        apiPage = apiFile.read()
    apiFile.close()

    row = []

    row.append(getNumericId(apiPage))
    row.append(getStringId(f))
    row.append(getName(apiPage))
    row.append(getSpecsField(apiPage,'API Provider'))
    row.append(getSpecsField(apiPage,'API Endpoint'))
    row.append(getSpecsField(apiPage,'API Homepage'))
    row.append(getSpecsField(apiPage,'Primary Category'))
    row.append(getNrFollowers(apiPage))
    row.append(getNrMashups(apiPage))
    row.append(getSpecsField(apiPage,'API Forum'))

    csvwriter.writerow(row)

    if i % 100 == 0:
        print >> sys.stderr, "done"
