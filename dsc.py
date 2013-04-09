import numpy as np
import network

class DSC_Parser(object):
        def __init__(self, filename, dataname=None):
                with open(filename, 'rb') as dsc:
                        self.data = dsc.readlines()

                self.network = network.Network()
                self._parse(self.data)
                
                #load an optional dataset as well
                if dataname:
                        self.dataset = self._loadData(dataname)

        def _parse(self, data):
                """Parse the DSC file format"""

                self.name = self.data[0].split()[-1]
                self._getNodes()
                self._getCPT()

        def _loadData(self, dataname):
                """Load an optional dataset along with dsc file"""
                
                data = np.recfromcsv(dataname, delimiter=",", names=True, autostrip=True, case_sensitive=True)
                net = self.network
                m, n = data.size, len(data.dtype.names)
                dataset = np.zeros((m, n), order='F')
                for node, d in net.node.iteritems():
                        dstates = d['states_ind']
                        dataset[:,net.graph['nilut'][node]] = [dstates[str(s)] for s in data[node]]
                        
                return dataset
                
        def _getNodes(self):
                """Extract all nodes from data"""

                for nline, line in enumerate(self.data):
                        if line.startswith('node'):
                                #split the line
                                line = line.split()
                                name = line[1]

                                self.network.add_node(name)
                                #advance the line one.
                                line = self.data[nline+1]
                                line = line.split()
                                
                                #get the number of states
                                self.network.node[name]['nstates'] = int(line[line.index("[")+1])
                                #get the state values
                                values = line[line.index("{")+1:line.index("};")]
                                values = (''.join(values)).split(',')
                                values = [t.replace('"', "") for t in values]
                                self.network.node[name]['ind_states'] = {ind:v for ind, v in enumerate(values)}
                                self.network.node[name]['states_ind'] = {k:v for v, k in self.network.node[name]['ind_states'].iteritems()}



        def _getCPT(self):
                """Extract the CPT table"""

                for nline, line in enumerate(self.data):
                        if line.startswith('probability'):
                                line = line.split()
                                name = line[line.index("(")+1]
                                
                                try:
                                        parents = line[line.index("|")+1:line.index(")")]
                                        parents = (''.join(parents)).split(',')
                                        self.network.add_edges_from([(p, name) for p in parents])
                                        parents = parents+[name]
                                        self.network.node[name]['cptdim'] = tuple(parents)
                                except ValueError:
                                        parents = [name]
                                        self.network.node[name]['cptdim'] = tuple(parents)


                                #create CPT table
                                cpt = np.zeros([self.network.node[x]['nstates'] for x in parents])

                                #grab the cptlines
                                i = 1
                                while line.count("}") == 0:
                                        l = self.data[nline+i].strip()
                                        if len(parents) > 1:
                                                index, vals = [t.strip() for t in l.split(':')]
                                                index = tuple([int(s) for s in index[1:-1].split(',')])
                                        else:
                                                index, vals = None, l.strip()

                                        vals = [float(v) for v in vals[:-1].split(',')]

                                        #print l, index, vals
                                        if index:
                                                cpt[index] = vals
                                        else:
                                                cpt[:] = vals
                                        i += 1
                                        line = self.data[nline+i]
                                self.network.node[name]['cpt'] = cpt


