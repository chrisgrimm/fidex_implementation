from typing import List
import tokens
from fidex_dag import FIDEX_node, FIDEX_edge, FIDEX_marking, FIDEX_DAG

def genDAG_nodes(s : str) -> List[FIDEX_node]:
    # make nodes for each entry in the string.
    nodes = [FIDEX_node([]) for _ in range(len(s)+1)]
    #nodes[0].marking = FIDEX_marking.START
    #nodes[len(s)].marking = FIDEX_marking.FINISH

    edge_mapping = dict()
    for i, node in enumerate(nodes):
        for j, other_node in enumerate(nodes):
            if i >= j:
                continue
            edge = FIDEX_edge(node, other_node, set())
            node.edges.append(edge)
            edge_mapping[(i,j)] = edge

    # get all the tokens that match
    matches = dict()
    for (i,j) in edge_mapping:
        for token in tokens.tokens:
            if not token.match(s[i:j]):
                continue
            if (i,j) in matches:
                matches[(i,j)].add(token)
            else:
                matches[(i,j)] = {token}

    # filter out the ones that we don't want
    i_list = sorted([i for (i,j) in edge_mapping.keys()])
    for i in i_list:
        j_list = sorted([j for (ii,j) in edge_mapping.keys() if ii == i], reverse=True)
        for j_idx, j in enumerate(j_list):
            for matched_token in matches[(i,j)]:
                for jj in j_list[j_idx+1:]:
                    try:
                        matches[(i,jj)].remove(matched_token)
                    except KeyError:
                        pass

    # apply the remaining matches to their edges
    for (i,j), edge in edge_mapping.items():
        for match in matches[(i,j)]:
            edge.W_set.add(match)

    return nodes

def mark_S1(nodes):
    nodes[0].add_marking(FIDEX_marking.START)

def mark_S2(nodes):
    for node in nodes[:-1]:
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