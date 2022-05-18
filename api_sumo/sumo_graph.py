#!/usr/bin/env python
"""

"""
from sumo_elems import Edge,Node

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class SumoGraph(object):
    def __init__(self):
        self.node_list = dict()
        self.edge_list = dict()
    
    def add_node(self,n):
#        if type(n) != Node:
#            raise TypeError('Arguments must be a node.')
        self.node_list[n.id] = n
    
    def get_node(self,id):
        return self.node_list[id]
    
    def in_node(self,n):
        return n in self.node_list
    
    def get_nodes(self):
        return self.node_list.keys()
    
    def iter_edges(self):
        return iter(self.edge_list.values())
    
    def add_edge(self,e):
#        if type(e) != Edge:
#            raise TypeError('Arguments must be a edge.')
        if not (e['from'] in self.node_list and e.to in self.node_list):
            raise ReferenceError('Edge nodes must be in the graph before.')
        self.edge_list[e.id] = e
    
    def get_edge(self,id):
        return self.edge_list[id]

    def in_edge(self,n):
        return n in self.edge_list
        
    def get_edges(self):
        return self.edge_list.keys()
    
    def iter_nodes(self):
        return iter(self.node_list.values())
    