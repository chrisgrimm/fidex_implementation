import genDAG
import fidex_dag
import tokens


cat_dag = genDAG.generate_startswith('cat')
dog_dag = genDAG.generate_startswith('dog')

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



combined_dag = fidex_dag.DAG_minus(cat_dag, dog_dag)
combined_dag.print_all_paths()
print(combined_dag.match('cat'))
print(combined_dag.match('dog'))