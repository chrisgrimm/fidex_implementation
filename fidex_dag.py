import numpy as np
import re
import tokens
from enum import Enum
from typing import Set, List, Tuple, Optional, Dict

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

    def has_marking(self, marking):
        return marking in self.markings

    def add_marking(self, marking):
        self.markings.add(marking)

    def remove_marking(self, marking):
        self.markings.remove(marking)

    def __str__(self):
        return f'Node({self.id})'

    def copy(self, node_lookup : Dict[int, 'FIDEX_node']):
        copy_node = FIDEX_node([], id=self.id)
        node_lookup[self.id] = copy_node
        for marking in self.markings:
            copy_node.add_marking(marking)
        for edge in self.edges:
            if edge.end.id in node_lookup:
                copy_end_node = node_lookup[edge.end.id]
            else:
                copy_end_node = edge.end.copy(node_lookup)
            new_edge = FIDEX_edge(copy_node, copy_end_node, edge.W_set.copy())
            copy_node.edges.append(new_edge)
        return copy_node


class FIDEX_DAG(object):

    def __init__(self, all_nodes : List[FIDEX_node]):
        self.all_nodes = all_nodes
        self.start_nodes = [node for node in all_nodes
                            if node.marking == FIDEX_marking.START]

    # currently we make a copy from all the nodes that are in
    def copy(self, tolerate_incomplete_copy=False) -> 'FIDEX_DAG':
        node_lookup = dict()
        [start_node.copy(node_lookup) for start_node in self.start_nodes]
        if not tolerate_incomplete_copy:
            for node in self.all_nodes:
                if node.id not in node_lookup:
                    raise Exception(f'Unreachable node.')
        new_all_nodes = [node_lookup[node.id] for node in self.all_nodes
                         if node.id in node_lookup]
        new_dag = FIDEX_DAG(new_all_nodes)
        return new_dag


def DAG_minus(orig_dag : FIDEX_DAG, minus_dag : FIDEX_DAG) -> FIDEX_DAG:
    orig_dag = orig_dag.copy()
    new_nodes = []
    for orig_node in orig_dag.start_nodes:
        for minus_node in minus_dag.start_nodes:
            new_node = DAG_minus_from_node(orig_node, minus_node, new_nodes)
            new_node.add_marking(FIDEX_marking.START)
            orig_node.remove_marking(FIDEX_marking.START)
    new_all_nodes = orig_dag.all_nodes + new_nodes
    # we could do a copy with incomplete tolerance here to "clean" up any newly
    # unreachable parts of the DAG, but I don't think it hurts very much to keep them around.
    new_dag = FIDEX_DAG(new_all_nodes).copy(tolerate_incomplete_copy=True)
    return new_dag


def DAG_minus_from_node(orig_node : FIDEX_node, minus_node : FIDEX_node,
                        new_nodes : List[FIDEX_node]) -> FIDEX_node:
    new_node = FIDEX_node([])
    new_nodes.append(new_node)
    if orig_node.has_marking(FIDEX_marking.FINISH) and not minus_node.has_marking(FIDEX_marking.FINISH):
        new_node.add_marking(FIDEX_marking.FINISH)
    for node_edge in orig_node.edges:
        for minus_edge in minus_node.edges:
            non_minus_condition = (node_edge.W_set.difference(minus_edge.W_set)).copy()
            minus_condition = (node_edge.W_set.intersection(minus_edge.W_set)).copy()
            non_minus_edge = FIDEX_edge(new_node, node_edge.end, non_minus_condition)
            minus_edge_node = DAG_minus_from_node(node_edge.end, minus_edge.end)
            minus_edge = FIDEX_edge(new_node, minus_edge_node, minus_condition)
            new_node.edges.append(non_minus_edge)
            new_node.edges.append(minus_edge)
    return new_node

def DAG_intersect(dag1 : FIDEX_DAG, dag2 : FIDEX_DAG) -> FIDEX_DAG:
    for node1 in dag1.all_nodes:
        for node2 in dag2.all_nodes:
            pass









