#Harmony search, Python
import numpy as N
from random import choice
import score
import cpt
import network
import itertools

class HarmonySearch(object):
    def __init__(self, net, hms=30, targetQuality=-N.inf, maxiters=500, hmcr=.95, par=.2, **kargs):
        """Harmony Search
        
        net: initial starting network.  If a number, a network of n nodes will
            be created and optimized
        objfunc: objective function.  Used to evaluate the quality of the network.
        hms: harmony memory size (will be used to create nxn matrix)
        maxiters = maximum number of iterations to run
        hmcr: harmony memory consideration rate.  Rate at which the memory will
            be considered when generating new solutions
        par: pitch adjustment rate.  Rate at which notes from memory will be
            adjusted when generating new solutions
        """
        if isinstance(net, int):
            self.net = network.Network(xrange(net))
        else:
            self.net = net
        self.black_edges = self.net.graph.get('black_edges', ())
        self.white_edges = self.net.edges()
        
        self.__dict__.update(kargs)
        self.n_nodes = len(self.net.nodes())
        self.maxiters = maxiters
        
        #harmony memory, a dictionary of elements.
        #Keyed by index, makes the hm a fixed size with fast lookup, insertion
        #useful for large hm.
        self.hms = hms
        self.par = par
        self.hmcr = hmcr
        
        #initial quality.
        self.targetQuality = targetQuality
        
    def _gen_random_harmony(self, nodes):
        net = network.random_network(nodes,
                                    required_edges=self.white_edges,
                                    prohibited_edges=self.black_edges)
        return net
        
    def _gen_random_instrument(self, indices=True):
        """Generate a random node [edge] that respects the blacklist"""
        n1, n2 = N.random.randint(self.n_nodes, size=(2,))
        edge = [self.net.graph['inlut'][n1], self.net.graph['inlut'][n2]]
        if indices is True:
            return edge, (n1, n2)
        return edge
        
    def _gen_random_note(self):
        edge, index = self._gen_random_instrument(indices=True)
        
        if edge not in self.black_edges:
            return edge
        elif edge.reverse() not in self.black_edges:
            return edge
        else:
            return ()
        
    def search(self, data, every=10, amnesia=50):
        """Harmony search in Python"""
        #harmony memory
        
        #cache network nodes and common functions
        nodes = self.net.nodes()
        Nshuf = N.random.shuffle
        stronglyconnected = network.is_strongly_connected
        
        def newHarmony(hm, net):
            #generate a new harmony [edgeset]
            
            #we loop through all possiblities for edges
            for n1 in nodes:
                for n2 in nodes:
                    if n1 == n2:
                        #continue on self-loops
                        continue
                    else:
                        randvals = N.random.rand(5)
                        
                        #consider harmony memory
                        if randvals[0] < self.hmcr:
                            #choose a random harmony from memory
                            hmedges = choice(hm).edge
                            #get the state of the edge.  If no edge return None
                            randedge = hmedges[n1].get(n2, None)
                            #define numerical value for state
                            if randedge is None:
                                case = 0 if randvals[4] < .5 else 2
                            else:
                                case = 1
                                
                            #perform a pitch adjustment
                            #choose an existing edge and reverse its direction
                            #but don't violate blacklist
                            #we can have 0. no edge 1. edge, 2. no edge 3. reverse edge
                            if randvals[1] < self.par:
                                #do we adjust up or down?
                                if randvals[2] < .5:
                                    #adjustment down
                                    case = (case - 1) % 4
                                else:
                                    #adjustment up
                                    case = (case + 1) % 4
                            
                            #apply the case
                            if case == 1 and (n1, n2) not in self.black_edges:
                                #add n1, n2 to edges
                                #but check strong connectedness
                                net.add_edge(n1, n2)
                                if not net.is_acyclic():
                                    #we are now cyclic
                                    net.remove_edge(n1, n2)
                            elif case == 3 and (n2, n1) not in self.black_edges:
                                #add n2, n1 to edges
                                net.add_edge(n2, n1)
                                if not net.is_acyclic():
                                    net.remove_edge(n2, n1)
                        else:
                            #ignore memory and get a single random note
                            if randvals[3] > .6666 and (n2, n1) not in self.black_edges:
                                #case == 3
                                net.add_edge(n2, n1)
                                if not net.is_acyclic():
                                    net.remove_edge(n2, n1)
                            elif randvals[3] < .3333 and (n1, n2) not in self.black_edges:
                                #case == 1
                                net.add_edge(n1, n2)
                                if not net.is_acyclic():
                                    net.remove_edge(n1, n2)
            
            return net
            
        hm = [self._gen_random_harmony(nodes) for i in xrange(self.hms)]
        maxiters = self.maxiters
        
        #score the memory
        print "Scoring Memory ",
        for n in hm:
            n.graph.update(self.net.graph)
            n.node.update(self.net.node)
            cpt.cpt(n, data)
            score.itlik(n, data)
            print ".",
        print "Done"
        
        #find worst and best network.
        hm.sort()
        worst = hm[0]
        best = hm[-1]
        
        #cache the initial network.  We reset the network to this state
        #each iteration.  Thus edges in the inital network work are considered
        #whitelisted edges
        self.initial = self.net.copy()
        while maxiters >= 0 and best.score < self.targetQuality:
            self.net.clear()
            self.net.add_edges_from(self.initial.edges())
            newHarmony(hm, self.net)
            cpt.cpt(self.net, data)
            score.itlik(self.net, data)
            if self.net > worst:
                hm[0] = self.net.copy()
                hm.sort()
                best, worst = hm[-1], hm[0]
            
            if maxiters % every == 0:
                print "Iteration {0}\tScore (b/w/c): {1}, {2}, {3}".format(maxiters, best.score, worst.score, self.net.score)
            
            if maxiters % amnesia == 0:
                #introduce amnesia into the system.
                amn = self._gen_random_harmony(nodes)
                amn.graph.update(self.initial.graph)
                amn.node.update(self.initial.node)
                cpt.cpt(amn, data)
                score.itlik(amn, data)
                
                if amn > worst:
                    hm[0] = amn.copy()
                    hm.sort()
                best, worst = hm[-1], hm[0]
            maxiters -= 1
        return best
        
        