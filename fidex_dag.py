import numpy as np
import re
import tokens
from enum import Enum
from typing import Set, List, Tuple, Optional

class FIDEX_marking(Enum):
    START = 1
    FINISH = 2
    NORMAL = 3

def make_generator():
    i = 0
    while True:
        yield i
        i += 1

id_generator = make_generator()



class FIDEX_edge(object):

    def __init__(self, start : 'FIDEX_node', end : 'FIDEX_node', W_set : Set[tokens.FIDEX_token]):
        self.W_set = W_set
        self.start = start
        self.end = end

    def __str__(self):
        return f'Edge({self.start}, {self.end})'

class FIDEX_node(object):

    def __init__(self, edges : List[FIDEX_edge], id=None):
        if id is None:
            self.id = next(id_generator)
        self.edges = edges
        self.markings = set()

    def is_marking(self, marking):
        return marking in self.markings

    def add_marking(self, marking):
        self.markings.add(marking)

    def remove_marking(self, marking):
        self.markings.remove(marking)

    def __str__(self):
        return f'Node({self.id})'

class FIDEX_DAG(object):

    def __init__(self, all_nodes : List[FIDEX_node]):
        self.all_nodes = all_nodes
        self.start_nodes = [node for node in all_nodes
                            if node.marking == FIDEX_marking.START]



