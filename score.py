import numpy as N
import util

def likelihood(net, data, nodes=()):
    """Calculate the log likelihood of a network
    
    PARAMETERS:
        net     A bayesian network
        data    The dataset corresponding to the network (numpy array)
        nodes   tuple of nodes to use calculating the log likelihood.
                (if empty, use the entire network)
        
    RETURNS:
        net.score       The log likelihood of the network.
                        Added as an attribute of the network.
    """
    
    #to calculate the log likelihood of net
    
    #we iterate through each entry in data
    #we look up the probability in the nodes cpt

    #build a lookup table for all the nodes based on their idb
    #this gives our column indices for the different variables
    ll = N.zeros(data.shape, order='F')
    predd = net.pred
    nodedict = net.node
    lut = net.graph['nilut']
    
    if nodes:
        iternodes = {n:i for n, i in lut.iteritems() if n in nodes or i in nodes}
    else:
        iternodes = lut
        
    for varl, vari in iternodes.iteritems():
        #build list of parents for current variable
        parents = predd[varl].keys()
        parents.append(varl)
        
        x = [lut[n] for n in parents]
        #build a state matrix
        states = data[:,x]
        varlcpt = nodedict[varl]['cpt']
        ll[:,vari] = [varlcpt[tuple(i)] for i in states]
        print N.any(ll[:,vari]==0)
    return ll
    net.score = N.sum(N.log(ll))
    return net.score
    
def itlik(net, data, optimal=-N.inf, nodes=()):
    """Iterteravely calculate likelihood
    
    keeps a running sum of likelihood of each node.  
    if likelihood drops below optimal, returns -inf
    
    PARAMETERS:
        net             A bayesian network
        data            Dataset to use in calculating the log likelihood
        optimal         cutoff value for log likelihood.
        nodes           Nodes to use in calculating the likelihood
        
    RETURNS:
        net.score       The log likelihood of the network.
                        Added as an attribute of the network.
    """
    predd = net.pred
    nodedict = net.node
    lut = net.graph['nilut']
    likelihood = 0.0
    nlog = N.log
    nsum = N.sum
    results = N.zeros(data.shape[0])
    
    if nodes:
        iternodes = {n:i for n, i in lut.iteritems() if n in nodes or i in nodes}
    else:
        iternodes = lut
    
    for varl, vari in iternodes.iteritems():
        parents = predd[varl].keys()
        parents.append(varl)
        
        x = [lut[n] for n in parents]
        
        #build a state matrix
        states = data[:,x]
        varlcpt = nodedict[varl]['cpt']
        results[:] = [varlcpt[tuple(i)] for i in states]
        likelihood += nsum(nlog(results))
        if likelihood < optimal:
            likelihood = -N.inf
            break
    net.score = likelihood
    return net.score
    
def ll_edges(net, data):
    for f, e in net.edges():
        net.edge[f][e] = itlik(net, data, nodes=(f, e))
        
def ll_edges2(net, data, edge):
    nodes = util.all_parents(net, edge)
    return itlik(net, data, nodes=nodes)