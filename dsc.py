"""
DSC file importer.  This will read and construct a baysesian network
described in DSC format.  An optional dataset may be loaded as well
"""

import numpy as np
import network

class DSC_Parser(object):
        def __init__(self, filename, dataname=None):
            """
            PARAMETERS:
                filename        dsc file to parse
                dataname        dataset to associate with resulting network
            
            RETURNS:
                instance of DSC_Parser class
            """
            with open(filename, 'rb') as dsc:
                    self._data = dsc.readlines()

            self.network = network.Network()
            self._parse(self._data)
            
            #load an optional dataset as well
            if dataname:
                    self.dataset = self._loadData(dataname)

        def _parse(self, data):
                """Parse the DSC file format
                
                PARAMETERS:
                    data        contents of the dsc file
                    
                RETURNS:
                    None
                """

                self.name = self._data[0].split()[-1]
                self._getNodes()
                self._getCPT()

        def _loadData(self, dataname):
                """Load an optional dataset along with dsc file
                
                PARAMETERS:
                    dataname    filename of optional dataset
                    
                RETURNS:
                    dataset     dataset in a numpy array
                """
                
                data = np.recfromcsv(dataname, delimiter=",", names=True, autostrip=True, case_sensitive=True)
                net = self.network
                m, n = data.size, len(data.dtype.names)
                dataset = np.zeros((m, n), order='F')
                for node, d in net.node.iteritems():
                        dstates = d['states_ind']
                        col = net.graph['nilut'][node]
                        dataset[:,col] = [dstates[str(s)] for s in data[node]]
                        
                return dataset
                
        def _getNodes(self):
                """Extract all nodes from data.  Modifies the network.
                
                PARAMETERS:
                    None
                    
                RETURNS:
                    None
                """

                for nline, line in enumerate(self._data):
                        if line.startswith('node'):
                                #split the line
                                line = line.split()
                                name = line[1]

                                self.network.add_node(name)
                                #advance the line one.
                                line = self._data[nline+1]
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
                """Extract the CPT table.  Modifies the network
                
                PARAMETERS:
                    None
                    
                RETURNS:
                    None
                """

                for nline, line in enumerate(self._data):
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
                                        l = self._data[nline+i].strip()
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
                                        line = self._data[nline+i]
                                self.network.node[name]['cpt'] = cpt


