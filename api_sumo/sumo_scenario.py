#!/usr/bin/env python
"""

"""

from sumo_elems import CarType,Vehicle,Flow,Route

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

class SumoScenario(object):
    def __init__(self):
        self.car_types = []
        self.routes = []
        self.flows = []
        self.vehicles = []
    
    def add_car_type(self,ct):
#        if type(ct) == CarType:
        self.car_types.append(ct)
    
    def add_route(self,rt):
#        if type(rt) == Route:
        self.routes.append(rt)
            
    def add_flow(self,fl):
#        if type(fl) == Flow:
        self.flows.append(fl)
            
    def add_vehicle(self,vh):
#        if type(vh) == Vehicle:
        self.vehicles.append(vh)
            
    def iter_car_types(self):
        return iter(self.car_types)
    
    def iter_routes(self):
        return iter(self.routes)
    
    def iter_flows(self):
        return iter(self.flows)
    
    def iter_vehicles(self):
        return iter(self.vehicles)