from fidex_dag import FIDEX_DAG, DAG_intersect, DAG_minus
from typing import List, Callable, Tuple

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
# def learn_disj_exprs_inc(D_tilde : List[FIDEX_DAG],
#                          D_tilde_minus : List[FIDEX_DAG],
#                          s : str,
#                          pred : Callable[[str], FIDEX_DAG]) -> Tuple[List[FIDEX_DAG], List[FIDEX_DAG]]:
#     D = pred(s)
#     if

