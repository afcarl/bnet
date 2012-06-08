import numpy as N
import network

import cpt
import score

"""A smart greedy learner.  Casts a net of random values far apart and chooses the net with the highest log likelihood as a starting place."""

class Learner(object):
    def __init__(self, data, initial=None):
        self.data = data
        self.initial = initial
    
    def run(self):
        pass
    
    
class Greedy(Learner):
    """A simple greedy learner"""
    
    def __init__(self, nodes, data, initial=None, nsamples=0, **kargs):
        super(Greedy, self).__init__(data, intial)
        self.nsamples = nsamples
        self.__dict__.update(kargs)
        self.stats = {restarts:-1, iterations:0, best_score=0}
        self.initial = initial
        self.data = data
        self.nodes = nodes
        
        
    def run(self):
        #make local variables of cpt and scoring functions
        _cpt = cpt.cpt
        _llik = score.likelihood
        
        #start with inital
        self._gen_initial()
        self.canditate = self.initial.copy()
        _cpt(self.candidate)
        _llik(self.candidate)
        self.candidate = _alter_network(self.candidate)
    
    def _alter_network(self, net, add_prob=.5):
        """Alter an edge randomly in the network"""
        
        
        if N.random.sample() < add_prob:
            #add a random edge
            nodes = N.random.randint(len(self.nodes), size=(2,))
            cnodes = (self.nodes[nodes[0]], self.nodes[nodes[1]])
            while cnodes in net.edges():
                nodes = N.random.randint(len(self.nodes), size=(2,))
                cnodes = (self.nodes[nodes[0]], self.nodes[nodes[1]])
            net.add_edge(cnodes[0], cnodes[1])
        else:
            #remove a random edge
            net.remove_edge(net.edges[N.random.randint(len(net.edges))])
            
        return net
        
        
    def _gen_random(self):
        """Generate a random network that will satisfy white and black lists if specified"""
        white = self.__dict__.get("wedges", ())
        black = self.__dict__.get("bedges", ())
        return network.random_network(self.nodes,
                                        required_edges=white
                                        prohibited_edges=black)
        
    def _gen_initial(self):
        if self.initial is not None:
            self.initial = self._gen_random()