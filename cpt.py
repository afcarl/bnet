import numpy as N

def cpt(net, data, nodes=None, bias=0.0):
    """
    Calculate conditional probability tables.  This function
    modifies the bayesian network.
    
    PARAMETERS:
        net     A Bayesian network
        data    A dataset

    RETURN:
        None
    """
    if nodes is not None:
        nodedict = {k:v for k,v in net.node.iteritems() if k in nodes}
    else:
        nodedict = net.node
    
    #clamp bias to [0.0, 1.0]
    if bias > 1.0:
        bias = 1.0
    elif bias < 0.0:
        bias = 0.0
    
    tiny = N.finfo(float).tiny
    predd = net.pred
    nlut = net.graph['nilut']
    nsum = N.sum
    data = N.atleast_2d(data)
    for n, d in nodedict.iteritems():
        #we need to check if cptdim already exists.
        in_edges = d.get('cptdim', predd[n].keys().append(n))
        numer = d.get('numer', N.zeros([net.node[x]['nstates'] for x in in_edges], dtype=int))
        denom = d.get('denom', N.zeros(numer.shape, dtype=int))
        #cpt = d.get('cpt', N.zeros(numer.shape, dtype=float))
        #print "Denom shape: ",denom.shape
        #numer = N.zeros([net.node[x]['nstates'] for x in in_edges])
        #denom = N.zeros(len(in_edges))
        #print "Calculating cpt for node: {0} (inedges: {1})".format(n, in_edges)
        in_edges_id = [nlut[x] for x in in_edges]
        for state in N.ndindex(numer.shape):
            matches = data[:,in_edges_id] == state
            z = nsum(matches.all(axis=1))
            y = nsum(matches[:,:-1].all(axis=1))
            #print "z:{0}\ty:{1}".format(z,y)
            #print state
            numer[state] += z
            denom[state] += y
            #cpt[state] = tiny if z == 0 or y == 0 else float(z)/y
        
        #try:
            #old = d['cpt']
            #tmp = N.absolute(old - cpt) * bias
            #cpt = N.where(old < cpt, cpt - tmp, cpt + tmp)
        #except KeyError:
            ##cpt table does not exist
            #pass
        
        #d['cpt'] = cpt
        d['numer'] = numer
        d['denom'] = denom
        d['cptdim'] = tuple(in_edges)

            