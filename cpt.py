import numpy as N

import multiprocessing as mp

def cpt(net, data, nodes=None, bias=0.0):
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
    for n, d in nodedict.iteritems():
        #we need to check if cptdim already exists.
        in_edges = d.get('cptdim', predd[n].keys().append(n))
        cpt = N.zeros([net.node[x]['nstates'] for x in in_edges])
        #print "Calculating cpt for node: {0} (inedges: {1})".format(n, in_edges)
        in_edges_id = [nlut[x] for x in in_edges]
        for state in N.ndindex(cpt.shape):
            matches = data[:,in_edges_id] == state
            z = nsum(matches.all(axis=1))
            y = nsum(matches[:,:-1].all(axis=1))
            #print "z:{0}\ty:{1}".format(z,y)
            cpt[state] = tiny if y == 0 or z == 0 else float(z)/y
        
        try:
            old = d['cpt']
            tmp = N.absolute(old - cpt) * bias
            cpt = N.where(old < cpt, cpt - tmp, cpt + tmp)
        except KeyError:
            #cpt table does not exist
            pass
        
        d['cpt'] = cpt
        d['cptdim'] = tuple(in_edges)
        

def multicpt(net, data, nodes=None):
    """Multiprocessing version of cpt"""
    
    if nodes is not None:
        nodedict = {k:v for k,v in net.node.iteritems() if k in nodes}
    else:
        nodedict = net.node
        
    #initialize Pool
    n = mp.cpu_count()
    n_nodes = nodedict.keys()
    
    #split network nodes into n parts
    avglen = len(n_nodes) / float(n)
    batches = []
    last = 0.0
    
    while last < len(n_nodes):
        batches.append(seq[int(last):int(last + avglen)])
        last += avglen
        
    p = mp.Pool(n)
    for b in batches:
        p.apply_async(cpt, args=(net,data,), kargs={nodes:b})
    p.close()
    p.join()
            