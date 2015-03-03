import network
import numpy as N
import random

def all_parents(net, nodes):
    """
    Return a set of immediate parent nodes of a set of nodes.
    
    PARAMETERS:
        net     A bayesian network
        nodes   a list of nodes for which parents are desired
        
    RETURNS:
        parentset       A set of all parents
    """
    if nodes:
        parentset = set(nodes)
        return parentset.union(*[all_parents(net, net.predecessors(node)) for node in nodes])
    else:
        return set()
        
def genRandObs(net, nobs, numeric=True):
    """generate valid random observations for net
    
    PARAMETERS:
        net     A bayesian network
        nobs    number of observations
        numeric generate numeric based observations (True)
                otherwise use labels (False)
    
    RETURNS:
        obslist list of random observations
    """
    
    _inlut = net.graph['inlut']
    _node = net.node
    _choice = random.choice
    _type = 'ind_states' if numeric else 'states_ind'
    
    obslist = []
    vars = len(_inlut.keys())
    for ol in xrange(nobs):
        ob = []
        for vl in xrange(vars):
            states = _node[_inlut[vl]][_type].keys()
            ob.append(_choice(states))
        obslist.append(ob)
    return obslist
    
def suspect(net, data, threshold=.01, output=None):
    """
    Find the most suspicious claims from jointprobs
    
    PARAMETERS:
        net             A bayesian network
        data            A dataset
        threshold=.01   Bottom threshold.  Default is least likely 1% of claims
        output=None     Optionally output to a file
        
    RETURNS:
        suspected       The suspected claims
        sortedind       The indices of the suspect claims in original dataset
    """
    jointprobs = net.jointprob(data)
    nprobs = jointprobs.shape[0]
    sortedind = N.argsort(jointprobs[:,-1].astype(float))
    suspicious = int(nprobs*threshold)
    print suspicious
    if suspicious >= 0:
        suspected = (jointprobs[sortedind])[:suspicious]
        sortedind = sortedind[:suspicious]
    else:
        suspected = (jointprobs[sortedind])[suspicious:]
        sortedind = sortedind[suspicious:]
    
    suspect_names = []
    _inlut = net.graph['inlut']
    m, n = suspected.shape[0], suspected.shape[1]-1
    for row in xrange(m):
        s_row = []
        for col in xrange(n):
            s_row.append(net.node[_inlut[col]]['ind_states'][suspected[row,col]])
        s_row.append(str(suspected[row, col+1]))
        suspect_names.append(s_row)
        
    if output is not None:
        with open(output, 'wb') as f:
            f.write(','.join([str(char) for char in net.ordering+["log prob"]]))
            f.write('\n')
            for obs in suspect_names:
                f.write(','.join([o for o in obs]))
                f.write('\n')
    
    return suspected, sortedind

def load_dataset(net, filename):
    """Turn a dataset into corresponding state indexes for network
    
    PARAMETERS:
        net             A bayesian network
        filename        file from which to load dataset
        
    RETURNS:
        numberdata      values of dataset in a numpy array
    """    
    
    data = N.recfromcsv(filename, delimiter=",", names=True, autostrip=True, case_sensitive=True)

    m, n = data.size, len(data.dtype.names)
    numberdata = N.zeros((m, n), order='F')
    
    for node, d in net.node.iteritems():
        states = d['states_ind']
        numberdata[:,net.graph['nilut'][node]] = [states[str(s)] for s in data[node]]
        
    return numberdata
    
def clearCPT(net):
    """Clear the CPT tables of each node in net
    
    PARAMETERS:
        net     A bayesian network
        
    RETURNS:
        None
    """
    
    for d in net.node.itervalues():
        if 'numer' in d:
            del d['numer']
        if 'denom' in d:
            del d['denom']
        if 'cpt' in d:
            del d['cpt']

def ajustRandom(net, dataset, obs=.25, vars=.1):
    """Adjust random parts of random observations
    
    Returns a list of indexes changed and a copy of the dataset with changes
    
    PARAMETERS:
        net     A bayesian network
        dataset A dataset (numpy array)
        obs     percentage of dataset to adjust
        vars    variance to adjust by
        
    RETURNS:
        observations    copy of dataset that has been adjusted
        randobs         indexes of dataset have have been changed
    """
    
    observations = dataset.copy()
    rows, cols = observations.shape
    
    ObsFactor = int(rows*obs) if obs <= 1 else obs
    VarsFactor = int(cols*vars) if vars <= 1 else vars
    
    randobs = N.random.randint(rows, size=ObsFactor)
    
    #iterate through each randomly selected observation
    inlut = net.graph['inlut']
    randint = N.random.randint
    for ob in randobs:
        #select a random variable
        randvars = randint(cols, size=VarsFactor)
        
        #iterate through each randomly selected variable
        for i, va in zip(randvars, (inlut[x] for x in randvars)):
            #get the possible states for variable
            states = net.node[va]['nstates']
            observations[ob, i] = randint(states)
            
    return observations, randobs
    
    