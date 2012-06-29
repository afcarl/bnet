import network
import numpy as N
import random

def all_parents(net, nodes):
    #Get all the parents of nodes
    if nodes:
        parentset = set(nodes)
        return parentset.union(*[all_parents(net, net.predecessors(node)) for node in nodes])
    else:
        return set()
        
def genRandObs(net, nobs):
    """generate valid random observations for net"""
    
    _inlut = net.graph['inlut']
    _node = net.node
    _choice = random.choice
    
    obslist = []
    vars = len(_inlut.keys())
    for ol in xrange(nobs):
        ob = []
        for vl in xrange(vars):
            states = _node[_inlut[vl]]['states'].keys()
            ob.append(_choice(states))
        obslist.append(ob)
    return obslist
    
def suspect(jointprobs, threshold=.01, output=None, vars=[]):
    """Find the most suspicious claims from jointprobs
    
    Default is least likely 1% of the claims
    If output is defined, will write results to a file
    """
    
    nprobs = jointprobs.shape[0]
    sortedprobs = jointprobs[N.argsort(jointprobs[:,-1].astype(float))]
    suspicious = int(nprobs*threshold)
    suspected = sortedprobs[:suspicious]
    if output is not None:
        if vars:
            with open(output, 'wb') as f:
                f.write(','.join([str(char) for char in vars+["log prob"]]))
                f.write('\n')
                for obs in suspected:
                    f.write(','.join([str(o) for o in obs]))
                    f.write('\n')
        else:
            raise ValueError("to output to a file, variable names must be specified")
    else:
        return suspected
    