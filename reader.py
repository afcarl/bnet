import network
import numpy as N

def csv2bnet(filename, names=True, numerize=True):
    """Read a csv file into and return a bnet object"""
    
    data = N.recfromcsv(filename, delimiter=",", names=names, autostrip=True)
    
    #make network with named nodes
    net = network.Network(data.dtype.names)
    
    m, n = data.size, len(data.dtype.names)
    dataset = N.zeros((m,n), order='F')
    #set up a map for each node that maps the states to an numeric value
    for node, d in net.node.iteritems():
        states = N.unique(data[node])
        d['nstates'] = states.size
        d['states'] = {stateID:name for stateID, name in enumerate(states)}
        tmplookup = {k:v for v, k in d['states'].iteritems()}
        dataset[:,net.graph['nilut'][node]] = [tmplookup[s] for s in data[node]]
    
    return net, dataset
    