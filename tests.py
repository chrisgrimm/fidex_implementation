import genDAG
import fidex_dag


cat_dag = genDAG.generate_startswith('cat')
oot_dag = genDAG.generate_startswith('dog')
combined_dag = fidex_dag.DAG_minus(cat_dag, oot_dag)
combined_dag.print_all_paths()

print(combined_dag.match(''))