import numpy as N
import networkx as nx
import itertools
import pydot

class NodeException(Exception): pass

class Network(nx.DiGraph):
    
    def __init__(self, nodes=(), edges=tuple(), score=None):
        """Creates a Network.
        
        nodes is a list of pebl.data.Variable instances.
        edges can be:
        
            * a list of edge tuples
            * an adjacency matrix (as boolean numpy.ndarray instance)
            * string representation (see Network.as_string() for format)
        
        """
        
        super(Network, self).__init__()
        #initialize the lut in graph
        self.graph['inlut'] = {}
        self.graph['nilut'] = {}
        self.add_nodes_from(nodes)

        if isinstance(edges, N.ndarray):
            #create edges using adj mat.
            edg = self._adjmat_to_edges(edges)
        elif isinstance(edges, str) and edges:
            edg = [map(int, x.split(",")) for x in edges.split(";")]
        else:
            edg = edges
            
        self.add_edges_from(edg)
        
        #this store the network score.
        #If None, network is not scored, otherwise this is a float
        self.score = score

    def __hash__(self):
        return hash(tuple(self.edges()))

    def __cmp__(self, other):
        return cmp(self.score, other.score)

    def __eq__(self, other):
        return self.score == other.score and hash(self.edges) == hash(other.edges)

    def _add_node_attr(self, node, attr, value):
        """Add an attr to a node's dictionary"""
        
        self.node[node][attr] = value
    
    def _next_lut(self, lut):
        """Return next available id in lut"""
        try:
            n = max(lut) + 1
        except ValueError:
            n = 0
        
        return n
    
    def _adjmat_to_edges(self, adjmat):
        """Convert adjmat to a tuple of edges"""
        rows,cols = adjmat.shape
        nodes = self.graph['inlut']
        
        return [(nodes[j],nodes[k]) for k in xrange(cols) for j in xrange(rows) if adjmat[j,k]]
    
    @property
    def ordering(self):
        lut = self.graph['inlut']
        return list(lut[n] for n in lut.iterkeys())
        
    @property
    def adj_mat(self):
        return nx.adjacency_matrix(self)
        
    def add_edges_from(self, edges, attr_dict=None, **attr):
        """Add edges from [edges] to the network
        
        Will fail if nodes being connected by edges don't exist"""
        
        if isinstance(edges, N.ndarray):
            edges = self._adjmat_to_edges(edges)
            
        for edge in edges:
            self.add_edge(edge[0], edge[1], attr_dict=attr_dict, **attr)
    
    def add_edge(self, u, v, attr_dict=None, **attr):
        """Add edge between nodes u and v.  u and v must exist otherwise exception is thrown"""
        
        u_exist = u in self.nodes()
        
        if u_exist and v in self.nodes():
            super(Network, self).add_edge(u, v, attr_dict=attr_dict, **attr)
        else:
            if u_exist:
                raise NodeException("Node {0} does not exist!".format(v))
            else:
                raise NodeException("Node {0} does not exist!".format(u))
    
    def clear(self):
        """Clear all edges from network, but keep nodes"""
        self.remove_edges_from(self.edges())
        
    def add_nodes_from(self, nodes, **attr):
        super(Network, self).add_nodes_from(nodes, **attr)
            
        #add the nodes to the lut
        n = self._next_lut(self.graph['inlut'])
        self.graph['inlut'] = {i:n for i, n in enumerate(nodes, n)}
        self.graph['nilut'] = {n:i for i, n in self.graph['inlut'].iteritems()}
        
    def add_node(self, n, **attr):
        super(Network, self).add_node(n, **attr)
        
        #add the nodes to the lut
        n = self._next_lut(self.graph['inlut'])
        self.graph['inlut'] = {i:n for i, n in enumerate(nodes, n)}
        self.graph['nilut'] = {n:i for i, n in self.graph['inlut'].iteritems()}
        
    def get_id(self, node):
        """Get id of a node"""
        return self.nodes().index(node)
                
    def get_node_by_id(self, id):
        """Get a node by id"""
        
        return self.nodes()[id]
        
    def get_node_subset(self, node_ids):
        """Return a subset of nodes from node ids"""
        return [n for n in nodes() if n in node_ids]
        #return dict((k, self.nodeids[k]) for k in node_ids)
        
    def is_acyclic(self):
        """Uses a depth-first search (dfs) to detect cycles."""

        return nx.is_directed_acyclic_graph(self)    
       
    def layout(self, prog="dot", args=''): 
        """Determines network layout using Graphviz's dot algorithm.

        width and height are in pixels.
        dotpath is the path to the dot application.

        The resulting node positions are saved in network.node_positions.

        """

        self.node_positions = nx.graphviz_layout(self, prog=prog, args=args)
    
    def as_dotstring(self):
        """Returns network as a dot-formatted string"""

        return self.as_pydot().to_string()

    def as_dotfile(self, filename):
        """Saves network as a dot file."""

        nx.write_dot(self, filename)

    def as_pydot(self):
        """Returns a pydot instance for the network."""

        return nx.to_pydot(self)
    
################################################################################
#Factory Functions
################################################################################
def random_network(nodes, required_edges=(), prohibited_edges=(), max_attempts=50):
    """Creates a random network with the given set of nodes.

    Can specify required_edges and prohibited_edges to control the resulting
    random network.  
    
    max_attempts sets how many times to try to achieve the criteria.
    If we use up all max_attempts we cut density in half and try again.
    """
    def _randomize(net, density=None):
        net.clear()
        n_nodes = len(net.nodes())
        nodes = net.graph['nilut']
        density = density or 1.0/n_nodes

        for attempt in xrange(max_attempts):
            # create an random adjacency matrix with given density
            adjmat = N.random.rand(n_nodes, n_nodes)
            adjmat[adjmat >= (1.0-density)] = 1
            adjmat[adjmat != 1] = 0
            
            # add required edges
            for src,dest in required_edges:
                adjmat[nodes[src], nodes[dest]] = 1

            # remove prohibited edges
            for src,dest in prohibited_edges:
                adjmat[nodes[src], nodes[dest]] = 0

            # remove self-loop edges (those along the diagonal)
            N.fill_diagonal(adjmat, 0)
            
            # set the adjaceny matrix and check for acyclicity
            net.add_edges_from(adjmat)

            if net.is_acyclic():
                return net

        # got here without finding a single acyclic network.
        # so try with a less dense network
        return _randomize(net, density=density/2.0)

    # -----------------------
    
    net = Network(nodes)
    
    return _randomize(net)
    
def randomDAG(nodes, white_edges=(), black_edges=(), prob=.5):
    """Generate a random DAG"""
    
    #shuffle the nodes
    N.random.shuffle(nodes)
    
    #add the white edges
    net = Network(nodes, white_edges)
    
    for e in itertools.combinations(nodes, 2):
        if N.random.randn() < prob:
            net.add_edge(*e)
    
    return net
    
def dist(net1, net2):
    """Return the distance between two networks
    Defined as how many edges must be added and removed to make net1==net2
    Networks must have the same number of nodes
    """
    x, y = map(nx.adj_matrix, (net1, net2))

    if x.shape != y.shape:
        if x.shape > y.shape:
            #make it so y is always >= to x
            tmp = x
            x = y
            y = tmp
            
        x_tmp = N.zeros(y.shape)
        for i, v in N.ndenumerate(x):
            x_tmp[i] = v
        x = x_tmp
        
    return N.sum(N.abs(x-y))
    
def is_strongly_connected(G):
    """Can be passed and edge dictionary or Graph"""
    if isinstance(G, dict):
        return len(G.keys()) == nx.strongly_connected.number_strongly_connected_components(G)
    else:
        return nx.strongly_connected.is_strongly_connected(G)