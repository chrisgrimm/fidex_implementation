from typing import Optional, Callable, Dict, List, Tuple, Set
from tokens import FIDEX_token
from fidex_dag import FIDEX_edge, FIDEX_DAG, FIDEX_node, FIDEX_marking
import itertools

new_node_gen = itertools.count()
get_new_node = lambda: next(new_node_gen)

class DAG2(object):

    def __init__(self):
        self.Q : Set[int] = set()
        self.E : Set[Tuple[int,int]] = set()
        self.W : Dict[Tuple[int,int], Set[FIDEX_token]] = dict()
        self.S : Set[int] = set()
        self.F : Set[int] = set()


    def copy(self):
        new_dag = DAG2()
        new_dag.Q = self.Q.copy()
        new_dag.E = self.E.copy()
        new_dag.W = {edge : s.copy() for edge, s in self.W.items()}
        new_dag.S = self.S.copy()
        new_dag.F = self.F.copy()
        return new_dag

    def convert_to_FIDEX_dag(self):
        # build the nodes
        node_mapping = {node_id : FIDEX_node([], id=node_id) for node_id in self.Q}
        # mark the nodes
        for node_id, node in node_mapping.items():
            if node_id in self.S:
                node.add_marking(FIDEX_marking.START)
            if node_id in self.F:
                node.add_marking(FIDEX_marking.FINISH)
        # add the edges to each node
        for (id1, id2) in self.E:
            edge = FIDEX_edge(node_mapping[id1], node_mapping[id2], self.W[(id1, id2)].copy())
            node_mapping[id1].edges.append(edge)
        return FIDEX_DAG(list(node_mapping.values()))

    def load_from_FIDEX_dag(self, dag : FIDEX_DAG):
        for node in dag.all_nodes:
            self.Q.add(node.id)
            if node.has_marking(FIDEX_marking.START):
                self.S.add(node.id)
            if node.has_marking(FIDEX_marking.FINISH):
                self.F.add(node.id)
            for edge in node.edges:
                self.E.add((edge.start.id, edge.end.id))
                self.W[(edge.start.id, edge.end.id)] = edge.W_set.copy()
        return self





def minus(d1 : DAG2, d2 : DAG2) -> DAG2:
    d = d1.copy()
    for s in d.S.copy():
        for s2 in d2.S.copy():
            # create a new node s_dots in D
            s_dots = get_new_node()
            d.Q = d.Q.union({s_dots})
            # make s_dots a start node and s a non-starting node
            d.S = d.S.difference({s})
            d.S = d.S.union({s_dots})
            # copy outgoing edges and update edge labels
            d.E = d.E.union({(s_dots, q) for (p, q) in d.E if p == s})
            for q in d.Q:
                d.W[(s_dots, q)] = d.W.get((s, q), set())
            # remove token sequences for (s, s2)
            sub_partial_dag(d, s, d2, s2)
    return d


def sub_partial_dag(d1 : DAG2, q1 : int, d2 : DAG2, q2 : int):
    iter1 = [(q1, q1_prime) for p, q1_prime in d1.E
             if p == q1]
    iter2 = [(q2, q2_prime) for p, q2_prime in d2.E
             if p == q2]
    for (q1, q1_prime) in iter1:
        for (q2, q2_prime) in iter2:
            # create a new node q1_dots_prime in D1
            q1_dots_prime = get_new_node()
            d1.Q = d1.Q.union({q1_dots_prime})
            # copy outgoing edges and update edge labels
            d1.E = d1.E.union({(q1_dots_prime, q1_prime_prime) for p, q1_prime_prime in d1.E
                               if p == q1_prime})
            for q in d1.Q:
                d1.W[(q1_dots_prime, q)] = d1.W.get((q1_prime, q), set())
            # connect q1 and q1_dots_prime
            d1.E = d1.E.union({(q1, q1_dots_prime)})
            # update edge labels
            d1.W[(q1,q1_dots_prime)] = d1.W[(q1,q1_prime)].intersection(d2.W[(q2, q2_prime)])
            d1.W[(q1,q1_prime)] = d1.W[(q1, q1_prime)].difference(d2.W[(q2,q2_prime)])
            # mark q1_dots_prime as an end node
            if q1_prime in d1.F:
                d1.F = d1.F.union({q1_dots_prime})
            # mark q1_dots_prime as a non-ending node (delete-paths)
            if q2_prime in d2.F:
                d1.F = d1.F.difference({q1_dots_prime})
            # remove token sequences for (q1_dots_prime, q2_prime)
            sub_partial_dag(d1, q1_dots_prime, d2, q2_prime)


