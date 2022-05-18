#!/usr/bin/env python
"""

"""

from api_sumo import SumoGraph,Node,Edge

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class ManhattanGraph(SumoGraph):
    def __init__(self,rows=3,cols=3,length=100):
        super(ManhattanGraph,self).__init__()
        self._rows = rows
        self._cols = cols
        self._lgth = length
        self._create_graph()

    @property
    def rows(self): return self._rows
    @property
    def cols(self): return self._cols
    @property
    def length(self): return self._lgth

    def _create_graph(self):
        nodef = '{}.{}'.format
        edgef = '{}/{}'.format

        #Crea un nodo en cada punto (fila,columna), excepto en las cuatro esquinas de la malla
        for i in range(self.rows):
            for j in range(self.cols):
                l = 1 if (0 < i < self.rows-1) and (0 < j < self.cols-1) else 0
                n = Node(nodef(i,j),
                         self.length*j,
                         self.length*(self.rows-1-i),
                         l)
                self.add_node(n)

        for i in range(1,self.rows-1):
            for j in range(1,self.cols-1):
                n0 = self.get_node(nodef(i,j))
                nN = self.get_node(nodef(i-1,j))
                nS = self.get_node(nodef(i+1,j))
                nW = self.get_node(nodef(i,j-1))
                nE = self.get_node(nodef(i,j+1))
                self.add_edge(Edge(edgef(n0.id,nN.id),n0,nN))
                self.add_edge(Edge(edgef(n0.id,nS.id),n0,nS))
                self.add_edge(Edge(edgef(n0.id,nW.id),n0,nW))
                self.add_edge(Edge(edgef(n0.id,nE.id),n0,nE))

        for i in range(1,self.rows-1):
            n0 = self.get_node(nodef(i,0))
            n1 = self.get_node(nodef(i,1))
            n2 = self.get_node(nodef(i,self.cols-2))
            n3 = self.get_node(nodef(i,self.cols-1))
            self.add_edge(Edge(edgef(n0.id,n1.id),n0,n1))
            self.add_edge(Edge(edgef(n3.id,n2.id),n3,n2))

        for i in range(1,self.cols-1):
            n0 = self.get_node(nodef(0,i))
            n1 = self.get_node(nodef(1,i))
            n2 = self.get_node(nodef(self.rows-2,i))
            n3 = self.get_node(nodef(self.rows-1,i))
            self.add_edge(Edge(edgef(n0.id,n1.id),n0,n1))
            self.add_edge(Edge(edgef(n3.id,n2.id),n3,n2))