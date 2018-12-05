from typing import List
import tokens
from tokens import FIDEX_token
from fidex_dag import FIDEX_node, FIDEX_edge, FIDEX_marking, FIDEX_DAG


def genDAG_nodes(s : str) -> List[FIDEX_node]:
    nodes = [FIDEX_node([]) for i in range(0, len(s)+1)]

    for i in range(len(s)):
        available_tokens = set(tokens.tokens)
        for j in range(len(s), i, -1):
            matched_tokens = {token for token in available_tokens
                              if token.match(s[i:j])}
            available_tokens = available_tokens.difference(matched_tokens)
            if len(matched_tokens) > 0:
                edge = FIDEX_edge(nodes[i], nodes[j], matched_tokens)
                nodes[i].edges.append(edge)
    return nodes

#genDAG_nodes2('cats')


def mark_S1(nodes):
    nodes[0].add_marking(FIDEX_marking.START)


def mark_S2(nodes):
    for node in nodes[:len(nodes)-1]:
        node.add_marking(FIDEX_marking.START)


def mark_F1(nodes):
    for node in nodes[1:]:
        node.add_marking(FIDEX_marking.FINISH)


def mark_F2(nodes):
    nodes[-1].add_marking(FIDEX_marking.FINISH)


def generate_startswith(s : str) -> FIDEX_DAG:
    nodes = genDAG_nodes(s)
    mark_S1(nodes)
    mark_F1(nodes)
    return FIDEX_DAG(nodes)


def generate_endswith(s : str) -> FIDEX_DAG:
    nodes = genDAG_nodes(s)
    mark_S2(nodes)
    mark_F2(nodes)
    return FIDEX_DAG(nodes)


def generate_matches(s : str) -> FIDEX_DAG:
    nodes = genDAG_nodes(s)
    mark_S1(nodes)
    mark_F2(nodes)
    return FIDEX_DAG(nodes)


def generate_contains(s : str) -> FIDEX_DAG:
    nodes = genDAG_nodes(s)
    mark_S2(nodes)
    mark_F1(nodes)
    return FIDEX_DAG(nodes)
