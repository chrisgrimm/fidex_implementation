from fidex_dag import FIDEX_DAG, DAG_intersect, DAG_minus, FIDEX_marking
from tokens import FIDEX_token
from genDAG import generate_startswith, generate_endswith, generate_contains, generate_matches

from typing import List, Callable, Tuple, Optional

def learn_token_seq(s_plus : List[str],
                    s_minus : List[str],
                    pred : Callable[[str], FIDEX_DAG]) -> FIDEX_DAG:
    D = pred(s_plus[0])
    for s in s_plus[1:]:
        D_plus = pred(s)
        D = DAG_intersect(D, D_plus)
    for s in s_minus:
        D_minus = pred(s)
        D = DAG_minus(D, D_minus)
    return D


def merge_DAGs(D_tilde):
    D_tilde_res = []
    D_tilde_res.append(D_tilde[0])
    for D in D_tilde:
        nonempty_intersection = None
        for j in range(len(D_tilde_res)):
            Dj = D_tilde_res[j]
            intersection = DAG_intersect(Dj, D)
            if not intersection.is_empty():
                nonempty_intersection = (j, intersection)
                break
        if nonempty_intersection is not None:
            (j, intersection) = nonempty_intersection
            D_tilde_res[j] = intersection
        else:
            D_tilde_res.append(D)
    return D_tilde_res


def learn_disj_exprs(s_plus : List[str],
                     s_minus : List[str],
                     pred : Callable[[str], FIDEX_DAG]) -> List[FIDEX_DAG]:
    D_tilde = []
    for s in s_plus:
        D_plus = pred(s)
        D_tilde.append(D_plus)
    for s in s_minus:
        D_minus = pred(s)
        for Di in D_tilde:
            Di = DAG_minus(Di, D_minus)
            if Di.is_empty():
                return []
    return merge_DAGs(D_tilde)


# TODO finish this part of the implementation
def learn_disj_exprs_inc(D_tilde : List[FIDEX_DAG],
                         D_tilde_minus : List[FIDEX_DAG],
                         s : str,
                         is_pos_str: bool,
                         pred : Callable[[str], FIDEX_DAG]) -> Tuple[List[FIDEX_DAG], List[FIDEX_DAG]]:
    D = pred(s)
    if is_pos_str:
        for D_minus in D_tilde_minus:
            D = DAG_minus(D, D_minus)
            if D.is_empty():
                return ([], D_tilde_minus)
        D_tilde.append(D)
    else:
        for i in range(len(D_tilde)):
            D_tilde[i] = DAG_minus(D_tilde[i], D)
            if D_tilde[i].is_empty():
                return ([], D_tilde_minus)
        D_tilde_minus.append(D)
    return (D_tilde, D_tilde_minus)


# returns the top ranked token sequence
def rank_DAG(D : FIDEX_DAG,
             score : Callable[[FIDEX_token], float]) -> List[FIDEX_token]:
    max_tok = dict()
    score_edge = dict()
    for e in D.edge_iterator():
        token_pairs = [(t, score(t)) for t in e.W_set]
        max_tok[e], score_edge[e] = max(token_pairs, key=lambda x: x[1])

    max_edge = dict()
    next_node = dict()
    score_node = dict()
    for q in D.node_iterator():
        edge_pairs = [(e, score_edge[e]) for e in q.edges]
        max_edge[q], score_node[q] = max(edge_pairs, key=lambda x: x[1])
        next_node[q] = max_edge[q].end

    start_pairs = [(s, score_node[s]) for s in D.start_nodes]
    q_c, avg_score = max(start_pairs, key=lambda x: x[1])
    q_c_prime = q_c
    path = [q_c]
    while (not q_c.has_marking(FIDEX_marking.FINISH)) or (avg_score < (len(path)*avg_score + score_node[q_c_prime])/(len(path) + 1)):
        q_c_prime = next_node[q_c]
        avg_score = (len(path) * avg_score + score_node[q_c_prime]) / (len(path) + 1)
        path.append(q_c_prime)
        q_c = q_c_prime

    ts = [max_edge[q] for q in path]
    return ts

def match_sequence(s : str, sequence : List[FIDEX_token]) -> bool:
    # TODO should I return False for empty sequences?
    if len(sequence) == 0:
        return s == ''
    for token in sequence:
        match = token.prefix_split_match(s)
        if match is None:
            return False
        (_, s) = match
    return True

class Disjunction(object):

    def __init__(self, sequences : List[List[FIDEX_token]]):
        self.sequences = sequences

    def match(self, s : str):
        return any(match_sequence(s, seq) for seq in self.sequences)

def rank_DAGs(D_tilde : List[FIDEX_DAG],
              score : Callable[[FIDEX_token], float]) -> Disjunction:
    seq_list = []
    for D in D_tilde:
        seq = rank_DAG(D, score)
        seq_list.append(seq)
    return Disjunction(seq_list)

def learn_filter(S_plus : List[str],
                 S_minus : List[str],
                 score : Callable[[FIDEX_token], float]) -> Optional[Disjunction]:
    pred_list = [generate_startswith, generate_endswith, generate_matches, generate_contains]
    for pred in pred_list:
        D_tilde, D_tilde_minus = learn_disj_exprs_inc([], [], S_plus[0], True, pred)
        if len(D_tilde) == 0:
            continue
        r = rank_DAGs(merge_DAGs(D_tilde), score)

        false_negatives = [s for s in S_plus if not r.match(s)]
        false_positives = [s for s in S_minus if r.match(s)]
        while len(false_negatives) > 0 or len(false_positives) > 0:
            if len(false_negatives) > 0:
                s = false_negatives[0]
                is_pos = True
            else:
                s = false_positives[0]
                is_pos = False
            D_tilde, D_tilde_minus = learn_disj_exprs_inc(D_tilde, D_tilde_minus, s, is_pos, pred)
            if len(D_tilde) == 0:
                break
            r = rank_DAGs(merge_DAGs(D_tilde), score)
            false_negatives = [s for s in S_plus if not r.match(s)]
            false_positives = [s for s in S_minus if r.match(s)]

        if len(D_tilde) != 0:
            return r
        else:
            return None


