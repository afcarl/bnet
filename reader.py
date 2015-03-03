import network
import numpy as N

def csv2bnet(filename, names=True, **kargs):
    """Read a csv file into and return a bnet object
    
    PARAMETERS:
        filename        CSV to use in creating network
        names           are the names of the nodes the first row?
        **kargs         additional arguments for numpy.recfromcsv
        
    RETURNS:
        net             instance of Network
        dataset         dataset as numpy array
    """
    
    data = N.recfromcsv(filename, delimiter=",", names=names, autostrip=True, case_sensitive=True, **kargs)
    
    #make network with named nodes
    net = network.Network(data.dtype.names)
    m, n = data.size, len(data.dtype.names)
    dataset = N.zeros((m, n), order='F')
    #set up a map for each node that maps the states to an numeric value
    for node, d in net.node.iteritems():
        states = N.unique(data[node])
        d['nstates'] = states.size
        dstates = {str(name):stateID for stateID, name in enumerate(states)}
        d['states_ind'] = dstates
        d['ind_states'] = {stateID:name for name, stateID in dstates.iteritems()}
        dataset[:,net.graph['nilut'][node]] = [dstates[str(s)] for s in data[node]]

    return [net, dataset]
    
def parsemodel(s, nodeorder=None, net=None):
    """Parse a modelstring to Bayes Net
    
    Format is as follows [Child|Parent:Parent:...]
    
    PARAMETERS:
        s               string representation of network
        nodeorder       string of all nodes separated by spaces
        net             Network instance to use in building network
        
    RETURN:
        Network         instance of Network
    """
    nodes = [t[:-1].split("|") for t in s.split("[") if t]
    
    if net is None:
        if isinstance(nodeorder, str):
            nodeorder = nodeorder.split()
        net = network.Network(nodeorder)
    for n in nodes:
        try:
            child, parents = n
            edges = [(p, child) for p in parents.split(":")]
            net.add_edges_from(edges)
        except ValueError:
            #no edge to add
            continue
    return net