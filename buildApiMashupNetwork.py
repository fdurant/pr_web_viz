import sys
import csv
import networkx as nx
from networkx.algorithms import bipartite
import random
import math

pathToApiCsvFile = sys.argv[1]
pathToMashupCsvFile = sys.argv[2]
pathToGraphMLFile = sys.argv[3]

print "pathToApiCsvFile: %s" % pathToApiCsvFile
print "pathToMashupCsvFile: %s" % pathToMashupCsvFile
print "pathToGraphMLFile: %s" % pathToGraphMLFile

G=nx.Graph()

def getRandomLongitude():
    return (random.random() * 360) - 180

def calcVizSize(nrFollowers, nrMashups, minSize=1, minStep=1):
    '''Returns a size for vizualization purposes'''
    nrFollowersWeight = 0.75
    nrMashupsWeight = 1 - nrFollowersWeight
    try:
        result = int(math.ceil(math.log((nrFollowersWeight * nrFollowers) + (nrMashupsWeight * nrMashups))))
    except ValueError:
        return minSize * minStep
    return (result + minSize) * minStep

with open(pathToApiCsvFile, 'rb') as apiCsvFile:
    apiCsvReader = csv.reader(apiCsvFile, delimiter=',')
    apiHeader = apiCsvReader.next()
    for apiRow in apiCsvReader:

        # Create a node for each API, using "apiIdString" as node ID
        G.add_node("api_%s" % apiRow[1])
        G.node["api_%s" % apiRow[1]]['label'] = apiRow[2]
        G.node["api_%s" % apiRow[1]]['bipartite'] = 0
#        G.node["api_%s" % apiRow[1]]['inapilist'] = True
        assert(int(apiRow[7]) >= 0), "Problem with apiNrFollowers for %s: '%s'" % (apiRow[1],apiRow[7])
        assert(int(apiRow[8]) >= 0), "Problem with apiNrMashups for %s: '%s'" % (apiRow[1],apiRow[8])
        G.node["api_%s" % apiRow[1]]['size'] = calcVizSize(int(apiRow[7]),int(apiRow[8]), minSize=3, minStep=4)
#        G.node["api_%s" % apiRow[1]]['lat'] = 23.439
#        G.node["api_%s" % apiRow[1]]['lon'] = getRandomLongitude()
        
        # And attach the attributes from the CVS file
        for c in range(len(apiRow)):
            fieldName = apiHeader[c]
            if fieldName in ['apiPrimaryCategory']:
                G.node["api_%s" % apiRow[1]][fieldName] = apiRow[c]
                

with open(pathToMashupCsvFile, 'rb') as mashupCsvFile:
    mashupCsvReader = csv.reader(mashupCsvFile, delimiter=',')
    mashupHeader = mashupCsvReader.next()
    for mashupRow in mashupCsvReader:

        # Create a node for each Mashup, using "mashupIdString" as node ID
        if not "mashup_%s" % mashupRow[1] in G.nodes():
            G.add_node("mashup_%s" % mashupRow[1])
            G.node["mashup_%s" % mashupRow[1]]['label'] = mashupRow[1]
            G.node["mashup_%s" % mashupRow[1]]['bipartite'] = 1
#            G.node["mashup_%s" % mashupRow[1]]['lat'] = -23.439
#            G.node["mashup_%s" % mashupRow[1]]['lon'] = getRandomLongitude()
#            print >> sys.stderr, "Added node for %s" % mashupRow[1]

            for c in range(len(mashupRow)):
                fieldName = mashupHeader[c]
                if fieldName == "relatedApiStringIds":
                    # Example of relatedApiStringIds field: youtube|yahoo-image-search|google-base
                    relatedApiStringIds = mashupRow[c].split('|')
#                    print >> sys.stderr, "relatedApiStringIds: ", relatedApiStringIds
                    for relatedApiStringId in relatedApiStringIds:
                        # Strangely, some mashups have no related API at all
                        if relatedApiStringId:
                            assert(G.node["mashup_%s" % mashupRow[1]]), "Missing mashup node: %s" % G.node[mashupRow[1]]
                            # Some referenced APIs are not in the API CSV file, e.g. because they are deprecated
                            # We add them nevertheless, but mark them as inapilist=False
                            if False and not "api_%s" % relatedApiStringId in G.nodes():
                                G.add_node("api_%s" % relatedApiStringId)
                                G.node["api_%s" % relatedApiStringId]['label'] = relatedApiStringId
                                G.node["api_%s" % relatedApiStringId]['bipartite'] = 0
#                                G.node["api_%s" % relatedApiStringId]['lat'] = 23.439
#                                G.node["api_%s" % relatedApiStringId]['lon'] = getRandomLongitude()
#                                G.node["api_%s" % relatedApiStringId]['inapilist'] = False
                                print >> sys.stderr, "WARNING: Added missing API node: %s" % relatedApiStringId
                            assert(len(relatedApiStringId) > 1), "len(%s) < 1 !!!" % relatedApiStringId
                            if "api_%s" % relatedApiStringId in G.nodes():
                                G.add_edge("mashup_%s" % mashupRow[1], "api_%s" % relatedApiStringId)
                elif fieldName == "mashupIdString":
                    # Skip this field
                    pass
                else:
                    # Add the field as an attribute to the newly created Mashup node
                    G.node["mashup_%s" % mashupRow[1]][fieldName] = mashupRow[c]

# Remove solitary (API as well as Mashup) nodes
solitary=[ n for n,d in G.degree_iter() if d==0 ]
G.remove_nodes_from(solitary)

sortedConnectedComponents = sorted(nx.connected_components(G), key = len, reverse=True)

cc = sortedConnectedComponents[0]
subGraph = G.subgraph(cc)
for n in subGraph.nodes():
    del subGraph.node[n]['bipartite']
print >> sys.stderr, "cc is bipartite: ", bipartite.is_bipartite(subGraph)
(apiPartition, mashupPartition) = bipartite.sets(subGraph)
apiWeightedGraph = bipartite.collaboration_weighted_projected_graph(subGraph, mashupPartition)


# Now only keep X times as many edges of the apiWeightedGraph
edge2nodeRatio = 100

nrNodes = len(apiWeightedGraph.nodes())
maxNrEdges = nrNodes * edge2nodeRatio

allEdgesSortedByWeight = sorted([e for e in apiWeightedGraph.edges_iter()], key=lambda e: apiWeightedGraph.edge[e[0]][e[1]]['weight'], reverse=False)

#print allEdgesSortedByWeight

cnt = 0
while cnt < len(allEdgesSortedByWeight) - maxNrEdges:
    e = allEdgesSortedByWeight[cnt]
    print >> sys.stderr, "Trying to remove edge (%s,%s) ... " % (e[0],e[1]),
    try:
        apiWeightedGraph.remove_edge(e[0],e[1])
        print >> sys.stderr, "done"
    except nx.exception.NetworkXError:
        pass
        print >> sys.stderr, "FAILED"
    cnt += 1

nx.write_graphml(apiWeightedGraph,pathToGraphMLFile)
