#Harmony search, Python
import numpy as N
from random import choice
import score
import cpt
import network

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
        
    def _gen_random_instrument(self):
        """Generate a random node [edge] that respects the blacklist"""
        n1, n2 = N.random.randint(self.n_nodes, size=(2,))
        edge = [self.net.graph['inlut'][n1], self.net.graph['inlut'][n2]]
        return edge
        
    def _gen_random_note(self):
        edge = self._gen_random_instrument()
        if edge not in self.black_edges:
            return edge
        elif edge.reverse() not in self.black_edges:
            return edge
        else:
            return ()
        
    def search(self, data, every=10):
        """Harmony search in Python"""
        #harmony memory
        
        def newHarmony(hm, nodes):
            #generate a new harmony [edgeset]
            edges = []
            for i in xrange(self.n_nodes):
                randvals = N.random.rand(3)
                
                #consider harmony memory
                if randvals[0] < self.hmcr:
                    #choose a random harmony
                    hmedges = choice(hm).edges()
                    #choose a random instrument
                    randinst = self._gen_random_instrument()
                    blacked = True if randinst in self.black_edges else False
                    revblacked = True if reversed(randinst) in self.black_edges else False
                    
                    #perform a pitch adjustment
                    #choose an existing edge and reverse its direction
                    #but don't violate blacklist
                    #we can have 0. no edge 1. edge, 2. reverse edge
                    if randvals[1] < self.par:
                        #do we adjust up or down?
                        cand_note = randinst[:]
                        if randvals[2] < .5:
                            #adjustment down
                            if randinst in hmedges:
                                #case 1 => case 0
                                #emit silence.  no edge
                                cand_note = ()
                            else:
                                #case 0 => case 2 -> case 1
                                #reverse edge
                                cand_note = cand_note.reverse() if not revblacked else ()
                                if not cand_note and blacked is False:
                                    #attempt to adjust down one more
                                    cand_note = randinst
                        else:
                            #adjustment up
                            if randinst in hmedges:
                                #case 1 => case 2 -> 0
                                #if reversed is blacklisted, shift up one more to case 0
                                cand_note = cand_note.reverse() if not revblacked else ()
                            else:
                                #case 0 => case 1 -> case 2
                                cand_note = randinst if not blacked else ()
                                if not cand_note and revblacked is False:
                                    cand_note = cand_note.reverse()
                                    
                        edges.append(cand_note)
                    else:
                        #don't adjust
                        if randinst not in self.black_edges:
                            edges.append(randinst)
                        else:
                            #emit silence
                            continue
                else:
                    #ignore memory and get a single random note
                    edges.append(self._gen_random_note())
            return edges
            
        nodes = self.net.node.keys()
        hm = sorted([self._gen_random_harmony(nodes) for i in xrange(self.hms)])
        maxiters = self.maxiters
        
        #score the memory
        print "Scoring Memory ",
        for network in hm:
            network.graph = self.net.graph.copy()
            network.node = self.net.node.copy()
            cpt.cpt(network, data)
            score.itlik(network, data)
            print ".",
        print
        
        #find worst and best network.
        worst = hm[0]
        best = hm[-1]
        
        #cache the initial network.  We reset the network to this state
        #each iteration.  Thus edges in the inital network work are considered
        #whitelisted edges
        self.initial = self.net.copy()
        
        while maxiters >= 0 and best.score < self.targetQuality:
            self.net = self.initial.copy()
            self.net.add_edges_from(newHarmony(hm, nodes))
            while not self.net.is_acyclic():
                self.net = self.initial.copy()
                self.net.add_edges_from(newHarmony(hm, nodes))
            cpt.cpt(self.net, data)
            score.itlik(self.net, data, optimal=worst.score)
            if self.net > worst:
                hm[0] = self.net.copy()
                hm.sort()
                best, worst = hm[-1], hm[0]
            
            if maxiters % every == 0:
                print "Iteration {0}\tScore (b/w/c): {1}, {2}, {3}".format(maxiters, best.score, worst.score, self.net.score)
            maxiters -= 1
        return best
        
        