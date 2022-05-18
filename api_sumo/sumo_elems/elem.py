#!/usr/bin/env python
"""
Basic object type to represent a sumo object in python.
"""
__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class Elem(object):
    def __init__(self,name,_id,d={},**args):
        # Name of the subclass
        super(Elem,self).__setattr__('name',name)
        # Id of any object
        super(Elem,self).__setattr__('id',_id)
        # Basic attribute container of any object
        super(Elem,self).__setattr__('attr',d)
        
    def __set_attr__(self,k,v):
        '''Extra method to add extra attributes to an object'''
        super(Elem,self).__setattr__(k,v)
    
    def __setitem__(self,key,value):
        '''To set items with brackets []'''
        self.__setattr__(key,value)
        
    def __getitem__(self,key):
        '''To get items with brackets []'''
        return self.__getattr__(key)
            
    def __setattr__(self,key,value):
        '''To set items with point p.e.  node.x = 0 to set attribute x of node object to 0'''
        if key not in self.attr:
            raise AttributeError(\
            'Set attribute error in {} {}'.format(type(self).__name__,self.id))
        self.attr[key] = value
    
    def __getattr__(self,key):
        '''To get items with point'''
        try:
            return self.attr[key]
        except KeyError:
            raise AttributeError(\
            'Get attribute error in {} {}'.format(type(self).__name__,self.id))
    
    def __str__(self):
        '''Return a string defining an object'''
        return 'Object {} with id: {}'.format(type(self).__name__,self.id)
    
    def __repr__(self):
        '''Return a string in xml/sumo format defining this object'''
        strlist = ['\t<{0}'.format(self.name)]
        strlist.append('id="{}"'.format(self.id))
        for key in self.attr:
            if self.attr[key] != None:
                strlist.append('{}="{}"'.format(key,self.attr[key]))
        strlist.append('/>\n')
        return ' '.join(strlist)