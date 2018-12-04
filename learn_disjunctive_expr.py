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
        found_j = False
        for j in range(len(D_tilde_res)):
            Dj = D_tilde_res[j]
            intersection = DAG_intersect(Dj, D)
            if not intersection.is_empty():
                D_tilde_res[j] = intersection
                found_j = True
                break
        if not found_j:
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
        if len(q.edges) == 0:
            score_node[q] = 0
            continue
        edge_pairs = [(e, score_edge[e]) for e in q.edges]
        max_edge[q], score_node[q] = max(edge_pairs, key=lambda x: x[1])
        next_node[q] = max_edge[q].end

    start_pairs = [(s, score_node[s]) for s in D.start_nodes]
    # there being no start pairs is an indication that the DAG is empty.
    if len(start_pairs) == 0:
        return []
    q_c, avg_score = max(start_pairs, key=lambda x: x[1])
    q_c_prime = q_c
    path = [q_c]
    while (not q_c.has_marking(FIDEX_marking.FINISH)) or (avg_score < (len(path)*avg_score + score_node[q_c_prime])/(len(path) + 1)):
        q_c_prime = next_node[q_c]
        avg_score = (len(path) * avg_score + score_node[q_c_prime]) / (len(path) + 1)
        path.append(q_c_prime)
        q_c = q_c_prime

    ts = [max_tok[max_edge[q]] for q in path if q in max_edge]

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


def learn_filter_no_disjunction(S_plus : List[str],
                                S_minus : List[str],
                                score : Callable[[FIDEX_token], float],
                                pred_list : List[Callable[[str], FIDEX_DAG]]) -> Optional[Disjunction]:
    #pred_list = [generate_startswith, generate_endswith, generate_matches, generate_contains]
    all_token_sequences = []
    for pred in pred_list:
        D = learn_token_seq(S_plus, S_minus, pred)
        token_seq = rank_DAG(D, score)
        all_token_sequences.append(token_seq)
    return Disjunction(all_token_sequences)




def learn_filter(S_plus : List[str],
                 S_minus : List[str],
                 score : Callable[[FIDEX_token], float],
                 pred_list : List[Callable[[str], FIDEX_DAG]]) -> Optional[Disjunction]:
    #pred_list = [generate_startswith, generate_endswith, generate_matches, generate_contains]
    for pred in pred_list:
        print('Adding:', S_plus[0], True)
        D_tilde, D_tilde_minus = learn_disj_exprs_inc([], [], S_plus[0], True, pred)
        if len(D_tilde) == 0:
            continue
        r = rank_DAGs(merge_DAGs(D_tilde), score)

        false_negatives = [s for s in S_plus if not r.match(s)]
        false_positives = [s for s in S_minus if r.match(s)]
        print(f'fn: {false_negatives}, fp: {false_positives}')
        while len(false_negatives) > 0 or len(false_positives) > 0:
            #print('false_negatives', false_negatives)
            #print('false_positives', false_positives)
            if len(false_negatives) > 0:
                s = false_negatives[0]
                is_pos = True
            else:
                s = false_positives[0]
                is_pos = False
            print('Adding:', s, is_pos)
            # TODO how can it be that negative examples dont change the false positive / negative splits sometimes but not othertimes.
            # TODO whats happening is this: A positive expression is being added, but its not successfully removing the false negative term. This results in the algorithm continually adding the same DAG.
            # weirdly, sometimes this seesm to change the tree and other times it doesnt. This means there is a source of noise in our code, maybe a set iteration or something that isnt deterministic.
            # this still seems like a bug if its possible to get different inclusions from randomness.

            D_tilde, D_tilde_minus = learn_disj_exprs_inc(D_tilde, D_tilde_minus, s, is_pos, pred)
            if len(D_tilde) == 0:
                break
            r = rank_DAGs(merge_DAGs(D_tilde), score)
            false_negatives = [s for s in S_plus if not r.match(s)]
            false_positives = [s for s in S_minus if r.match(s)]
            print(f'fn: {false_negatives}, fp: {false_positives}')

        if len(D_tilde) != 0:
            return r
        else:
            return None


