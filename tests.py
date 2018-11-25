import genDAG
import fidex_dag
import tokens
import pandas as pd
from termcolor import colored
from typing import List, Callable
from DAG2 import DAG2, minus


#cat_dag = genDAG.generate_startswith('cat')
end_a = genDAG.generate_endswith('aa')
#old_set = set([tuple(x) for x in end_a.get_all_paths()])

#d2_end_a = DAG2().load_from_FIDEX_dag(end_a)
#end_a2 = d2_end_a.convert_to_FIDEX_dag()
#new_set = set([tuple(x) for x in end_a2.get_all_paths()])
#print('set equality', new_set == old_set)


start_b = genDAG.generate_startswith('bb')
#d2_start_b = DAG2().load_from_FIDEX_dag(start_b)

q = [fidex_dag.FIDEX_node([]) for _ in range(6)]
# build D1
e = fidex_dag.FIDEX_edge(q[0], q[1], {tokens.letters['a'], tokens.letters['b']})
q[0].add_marking(fidex_dag.FIDEX_marking.START)
q[0].edges.append(e)
e = fidex_dag.FIDEX_edge(q[1], q[2], {tokens.letters['c'], tokens.letters['d']})
q[1].edges.append(e)
q[2].add_marking(fidex_dag.FIDEX_marking.FINISH)

D1 = fidex_dag.FIDEX_DAG([q[0],q[1],q[2]])


# build D2
e = fidex_dag.FIDEX_edge(q[3], q[4], {tokens.letters['a']})
q[3].edges.append(e)
q[3].add_marking(fidex_dag.FIDEX_marking.START)
e = fidex_dag.FIDEX_edge(q[4], q[5], {tokens.letters['c']})
q[4].edges.append(e)
q[5].add_marking(fidex_dag.FIDEX_marking.FINISH)

D2 = fidex_dag.FIDEX_DAG([q[3], q[4], q[5]])


#combined_dag = fidex_dag.DAG_minus(D1, D2)
#combined_dag.print_all_paths()

def print_path_diagram(dags : List[fidex_dag.FIDEX_DAG], assertion_function : Callable[[List[bool]], bool]):
    all_paths = []
    for dag in dags:
        all_paths.extend([tuple(x) for x in dag.get_all_paths()])
    all_paths = list(set(all_paths))
    path_sets = []
    for dag in dags:
        path_sets.append(set([tuple(x) for x in dag.get_all_paths()]))

    all_inclusions = []
    for path in all_paths:
        inclusions = []
        for path_set in path_sets:
            inclusions.append(path in path_set)
        all_inclusions.append(inclusions)
    for path, inclusions in zip(all_paths, all_inclusions):
        assertion_res = assertion_function(inclusions)
        if 'EMPTY' in path:
            text = colored('EMPTY', 'yellow')
        else:
            text = colored('SUCCESS', 'green') if assertion_res else colored('FAILURE', 'red')


        print(path, inclusions, text)


#combined_dag = fidex_dag.DAG_minus(cat_dag, dog_dag)
#combined_dag = fidex_dag.DAG_intersect(start_b, end_a)
#d2_combined = minus(d2_start_b, d2_end_a)
combined_dag = fidex_dag.DAG_minus(start_b, end_a)
#combined_dag = d2_combined.convert_to_FIDEX_dag()
#combined_dag.print_all_paths()
print_path_diagram([start_b, end_a, combined_dag], lambda x: (x[0] and (not x[1])) == x[2])
#print_path_diagram([start_b, end_a, combined_dag], lambda x: (x[0] and x[1]) == x[2])

print(combined_dag.match('bb'))
print(combined_dag.match('aa'))
print(combined_dag.match('bbaa')) # this should be false.
print(combined_dag.match('aabb')) # this should be true.
#combined_dag.match(start_b)
#combined_dag.print_all_paths()
