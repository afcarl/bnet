import network


def all_parents(net, nodes):
    #Get all the parents of nodes
    if nodes:
        parentset = set(nodes)
        return parentset.union(*[all_parents(net, net.predecessors(node)) for node in nodes])
    else:
        return set()