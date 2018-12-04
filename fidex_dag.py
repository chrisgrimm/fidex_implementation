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
        self.leads_no_where = False



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

    def edge_iterator(self):
        for edge in self.edges:
            yield edge
            yield from edge.end.edge_iterator()



    def node_iterator(self):
        yield self
        for edge in self.edges:
            yield from edge.end.node_iterator()

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

    def edge_iterator(self):
        for node in self.start_nodes:
            yield from node.edge_iterator()

    def node_iterator(self):
        for node in self.start_nodes:
            yield from node.node_iterator()

    def print_all_paths(self):
        for node in self.start_nodes:
            node.path_printer([])

    def get_all_paths(self):
        all_paths = []
        for node in self.start_nodes:
            node.path_getter([], all_paths)
        return all_paths


    # currently we make a copy from all the nodes that are in
    def copy(self, tolerate_incomplete_copy=True) -> 'FIDEX_DAG':
        node_lookup = dict()
        nodes_to_copy = set([node.id for node in self.start_nodes])
        mapping = {node.id : node for node in self.start_nodes}
        while len(nodes_to_copy) > 0:
            node_id = next(iter(nodes_to_copy))
            node = mapping[node_id]
            node.copy(node_lookup)
            copied_so_far = set(node_lookup.keys())
            nodes_to_copy = nodes_to_copy.difference(copied_so_far)

        #[start_node.copy(node_lookup) for start_node in self.start_nodes]
        if not tolerate_incomplete_copy:
            for node in self.all_nodes:
                if node.id not in node_lookup:
                    raise Exception(f'Unreachable node.')
        new_all_nodes = [node_lookup[n_node.id] for n_node in self.all_nodes
                         if n_node.id in node_lookup]
        new_dag = FIDEX_DAG(new_all_nodes)
        return new_dag


# remove nodes that dont lead anywhere
def DAG_leads_to_finish(edge : FIDEX_edge):
    if edge.end.has_marking(FIDEX_marking.FINISH):
        return True
    else:
        leads_to_finish = False
        for next_edge in edge.end.edges:
            other_edge = DAG_leads_to_finish(next_edge)
            leads_to_finish = leads_to_finish or other_edge
        if not leads_to_finish:
            edge.leads_no_where = True
            return False
        else:
            return True

def DAG_prune_node(node : FIDEX_node):
    node.edges = [edge for edge in node.edges if not edge.leads_no_where]

    for edge in node.edges:
        DAG_prune_node(edge.end)

def DAG_collect_reachable_nodes(node : FIDEX_node, collection : Set[FIDEX_node]):
    collection.add(node)
    for edge in node.edges:
        DAG_collect_reachable_nodes(edge.end, collection)

def DAG_prune(dag : FIDEX_DAG):
    dag = dag.copy()
    # mark the edges to be deleted.
    for node in dag.start_nodes:
        for edge in node.edges:
            DAG_leads_to_finish(edge)
    # remove marked edges.
    for node in dag.start_nodes:
        DAG_prune_node(node)

    reachable_set = set()
    for node in dag.start_nodes:
        if len(node.edges) == 0:
            continue
        DAG_collect_reachable_nodes(node, reachable_set)

    dag.all_nodes = list(reachable_set)
    dag.start_nodes = [node for node in dag.all_nodes if node.has_marking(FIDEX_marking.START)]
    return dag






def DAG_minus(orig_dag : FIDEX_DAG, minus_dag : FIDEX_DAG) -> FIDEX_DAG:
    orig_dag = orig_dag.copy()
    new_nodes = []
    for orig_node in orig_dag.start_nodes:
        for minus_node in minus_dag.start_nodes:
            new_node = DAG_minus_from_node(orig_node, minus_node, new_nodes)
            new_node.add_marking(FIDEX_marking.START)
            if orig_node.has_marking(FIDEX_marking.START):
                orig_node.remove_marking(FIDEX_marking.START)
            # TODO : it is questionable whether or not this line is necessary.
            # it might result in a "cleaner" tree.
            orig_node = new_node
    new_all_nodes = orig_dag.all_nodes + new_nodes
    new_dag = FIDEX_DAG(new_all_nodes)
    new_dag = DAG_prune(new_dag)
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
        # TODO why do I copy here?
        for node_edge in new_node.edges[:]:
            non_minus_condition = (node_edge.W_set.difference(minus_edge.W_set)).copy()
            minus_condition = (node_edge.W_set.intersection(minus_edge.W_set)).copy()
            node_edge.W_set = non_minus_condition
            if len(minus_condition) > 0:
                minus_edge_node = DAG_minus_from_node(node_edge.end, minus_edge.end, new_nodes)
                new_minus_edge = FIDEX_edge(new_node, minus_edge_node, minus_condition)
                new_node.edges.append(new_minus_edge)
        # clean up edges that have no tokens.
        new_node.edges = [edge for edge in new_node.edges if len(edge.W_set) > 0]
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
    dag = FIDEX_DAG(all_nodes)
    dag = DAG_prune(dag)
    return dag