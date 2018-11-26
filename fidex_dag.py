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
        return f'Edge({self.start}, {self.end}, {self.W_set})'

class FIDEX_node(object):

    def __init__(self, edges : List[FIDEX_edge], id=None):
        if id is None:
            self.id = next(id_generator)
        else:
            self.id = id
        self.edges = edges
        self.markings = set()

    def has_marking(self, marking):
        return marking in self.markings

    def add_marking(self, marking):
        self.markings.add(marking)

    def get_edge(self, start_id : int, end_id : int) -> Optional[FIDEX_edge]:
        for edge in self.edges:
            if edge.start.id == start_id and edge.end.id == end_id:
                return edge
        return None

    def remove_marking(self, marking):
        self.markings.remove(marking)

    def path_printer(self, current_path : List[tokens.FIDEX_token]):
        if self.has_marking(FIDEX_marking.FINISH):
            print(current_path)
        for edge in self.edges:
            if len(edge.W_set) == 0:
                return
                #edge.end.path_printer(current_path + ['EMPTY'])
            for w in edge.W_set:
                edge.end.path_printer(current_path + [w])

    def path_getter(self, current_path : List[tokens.FIDEX_token], gotten_paths : List[List[tokens.FIDEX_token]]):
        if self.has_marking(FIDEX_marking.FINISH):
            gotten_paths.append(current_path)
        for edge in self.edges:
            if len(edge.W_set) == 0:
                return
                #edge.end.path_getter(current_path + ['EMPTY'], gotten_paths)
            for w in edge.W_set:
                edge.end.path_getter(current_path + [w], gotten_paths)

    def match(self, s : str) -> bool:
        if s == '' and self.has_marking(FIDEX_marking.FINISH):
            return True
        for edge in self.edges:
            for token in edge.W_set:
                split = token.prefix_split_match(s)
                if split is None:
                    continue
                else:
                    # if the rest is '' and the node is a finish node, it's a match.
                    (match, rest) = split
                    did_match = edge.end.match(rest)
                    if did_match:
                        return True
                    else:
                        continue
        return False


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
                            if node.has_marking(FIDEX_marking.START)]

    def match(self, s : str) -> bool:
        for node in self.start_nodes:
            if node.match(s):
                return True
        return False

    def is_empty(self):
        # TODO: need to check that this is a sufficient condition for emptiness.
        return len(self.start_nodes) == 0

    def print_all_paths(self):
        for node in self.start_nodes:
            node.path_printer([])

    def get_all_paths(self):
        all_paths = []
        for node in self.start_nodes:
            node.path_getter([], all_paths)
        return all_paths


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
            if orig_node.has_marking(FIDEX_marking.START):
                orig_node.remove_marking(FIDEX_marking.START)
            orig_node = new_node
    new_all_nodes = orig_dag.all_nodes + new_nodes
    new_dag = FIDEX_DAG(new_all_nodes)
    return new_dag


def DAG_minus_from_node(orig_node : FIDEX_node, minus_node : FIDEX_node,
                        new_nodes : List[FIDEX_node]) -> FIDEX_node:
    # copy the original node and add it to the list of created nodes.
    new_node = FIDEX_node([])
    edges = [FIDEX_edge(new_node, edge.end, edge.W_set.copy()) for edge in orig_node.edges]
    new_node.edges = edges
    new_nodes.append(new_node)

    if orig_node.has_marking(FIDEX_marking.FINISH) and not minus_node.has_marking(FIDEX_marking.FINISH):
        new_node.add_marking(FIDEX_marking.FINISH)

    for minus_edge in minus_node.edges:
        for node_edge in new_node.edges[:]:
            non_minus_condition = (node_edge.W_set.difference(minus_edge.W_set)).copy()
            minus_condition = (node_edge.W_set.intersection(minus_edge.W_set)).copy()
            node_edge.W_set = non_minus_condition
            if len(minus_condition) > 0:
                minus_edge_node = DAG_minus_from_node(node_edge.end, minus_edge.end, new_nodes)
                minus_edge = FIDEX_edge(new_node, minus_edge_node, minus_condition)
                new_node.edges.append(minus_edge)
        # clean up edges that have no tokens.
        new_node.edges = [edge for edge in new_node.edges
                          if len(edge.W_set) > 0]
    return new_node

def DAG_intersect_from_node(node1 : FIDEX_node, node2 : FIDEX_node,
                            node_dict : Dict[Tuple[int,int],FIDEX_node]) -> FIDEX_node:
    # grab the node from the store if possible, otherwise create it.
    if (node1.id, node2.id) in node_dict:
        return node_dict[(node1.id, node2.id)]
    new_node = FIDEX_node([])
    node_dict[(node1.id, node2.id)] = new_node
    # set the start / finish markings of the new node.
    if node1.has_marking(FIDEX_marking.START) and node2.has_marking(FIDEX_marking.START):
        new_node.add_marking(FIDEX_marking.START)
    if node1.has_marking(FIDEX_marking.FINISH) and node2.has_marking(FIDEX_marking.FINISH):
        new_node.add_marking(FIDEX_marking.FINISH)
    # build the edges of the new node
    for node1_edge in node1.edges:
        for node2_edge in node2.edges:
            new_W_set = (node1_edge.W_set.intersection(node2_edge.W_set)).copy()
            if len(new_W_set) > 0:
                end_node = DAG_intersect_from_node(node1_edge.end, node2_edge.end, node_dict)
                new_edge = FIDEX_edge(new_node, end_node, new_W_set)
                new_node.edges.append(new_edge)
    return new_node

def DAG_intersect(dag1 : FIDEX_DAG, dag2 : FIDEX_DAG) -> FIDEX_DAG:
    node_dict = dict()
    for node1 in dag1.all_nodes:
        for node2 in dag2.all_nodes:
            DAG_intersect_from_node(node1, node2, node_dict)
    all_nodes = list(node_dict.values())
    return FIDEX_DAG(all_nodes)