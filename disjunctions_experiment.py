from typing import Callable, Tuple, List, Optional
from learn_disjunctive_expr import Disjunction, learn_filter, learn_filter_no_disjunction, pred_bindings
from genDAG import generate_startswith, generate_endswith, generate_matches, generate_contains
from tokens import generality_score, FIDEX_token
from instances import instances
from fidex_dag import FIDEX_DAG
from threading import Thread
from multiprocessing import Process
from tempfile import TemporaryFile
import pickle
import time
import os


def learn_instance(instance : Tuple[List[str], List[str]],
                   learn_filter_func,
                   pred_bindings):

    start = time.time()

    positive, negative = instance

    positive_sample = [positive[0]]
    negative_sample = []
    while True:
        disj = learn_filter_func(positive_sample, negative_sample, generality_score, pred_bindings)
        if disj is not None:
            filtered_positive = set([p for p in (positive+negative) if disj.match(p)])
            filtered_negative = set([p for p in (positive+negative) if not disj.match(p)])
            actual_positive = set(positive)
            actual_negative = set(negative)
            missing_positives = sorted(list(actual_positive.difference(filtered_positive)))
            missing_negatives = sorted(list(actual_negative.difference(filtered_negative)))
            if len(missing_positives) > 0:
                positive_sample.append(missing_positives[0])
            elif len(missing_negatives) > 0:
                negative_sample.append(missing_negatives[0])
            else:
                break
        else:
            raise Exception("AHHH")

    end = time.time()

    result = {
        'time_elapsed': end - start,
        'num_positive_samples': len(positive_sample),
        'num_negative_samples': len(negative_sample),
        'num_disjunctions': len(disj.sequences),
    }
    return result


def learn_instance_timeout(instance : Tuple[List[str], List[str]],
                           learn_filter_func,
                           pred_bindings,
                           seconds : int):
    process = Process(target=learn_instance, args=(instance, learn_filter_func, pred_bindings))
    with open('result.txt', 'wb') as f:
        pickle.dump(None, f)
    process.start()
    time.sleep(seconds)
    process.terminate()
    with open('result.txt', 'rb') as f:
        result = pickle.load(f)
    return result


def get_data(instances : List[Tuple[List[str], List[str]]]):
    timeout = 1000
    pred_sets = [('StartsWith', [pred_bindings['StartsWith']]),
                 ('EndsWith', [pred_bindings['EndsWith']]),
                 ('Matches', [pred_bindings['Matches']]),
                 ('Contains', [pred_bindings['Contains']]),
                 ('All', [pred_bindings['StartsWith'], pred_bindings['EndsWith'], pred_bindings['Matches'], pred_bindings['Contains']])]

    learn_filter_funcs = [('FIDEX', learn_filter),
                          ('NoDisj', learn_filter_no_disjunction)]

    data = {'FIDEX': {'StartsWith': [],
                      'EndsWith': [],
                      'Matches': [],
                      'Contains': [],
                      'All': []},
            'NoDisj': {'StartsWith': [],
                       'EndsWith': [],
                       'Matches': [],
                       'Contains': [],
                       'All': []}}
    for (filter_func_name, learn_filter_func) in learn_filter_funcs:
        for (pred_set_name, pred_set) in pred_sets:
            for i, instance in enumerate(instances):
                #if not (filter_func_name == 'FIDEX' and pred_set_name == 'EndsWith'):
                #    continue
                print(f'{filter_func_name}/{pred_set_name}/{i}')
                #result = learn_instance_timeout(instance, learn_filter_func, pred_set, timeout)
                result = learn_instance(instance, learn_filter_func, pred_set)
                print(f'\t{result}')
                data[filter_func_name][pred_set_name].append(result)
    with open(os.path.join('experiment_data', 'perf_data.pickle'), 'wb') as f:
        pickle.dump(data, f)


if __name__ == '__main__':
    get_data(instances)




