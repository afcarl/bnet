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