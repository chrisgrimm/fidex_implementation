from learn_disjunctive_expr import learn_filter, Disjunction, pred_bindings
from tokens import FIDEX_token
from tokens import generality_score
from genDAG import generate_startswith, generate_endswith, generate_matches, generate_contains
from fidex_dag import DAG_minus, DAG_intersect
import os

#word_bank = ['Cat123', 'CatABC', 'Cat423', 'Cat222', 'CatCDE', 'CatEHA', 'Cat132']
#word_bank = ['CatDogCat', 'CaDogCat', 'ArgleDogBarg', '12432', '1023432', 'BirdCart',
#             'DogDog', 'BirdCat', 'Dog', 'Doggy', 'CatCat', '1234', 'Dogo', 'Cat' ,'CatCatCatCatCat', 'CatCatCatCatCatCat', 'DogDogDog']

word_bank = os.listdir('/Users/chris/projects/q_learning/runs/')
print(word_bank)

#positive_words = ['cat1', 'cat2', 'cat3', 'cat4']
#negative_words = ['dog1', 'dog2', 'dog3', 'dog4']

positive_words = ['Robert M. Smith', 'John E. Doe', 'James F. Franco', 'Wesley W. Weimer']
negative_words = ['John Stuart', 'Jimmy Mcgill', 'Johnny Walker', 'Jeffrey Dahmer']

#positive_words = ['123cats456', 'cats', 'asdcats12312']
#negative_words = ['asdfsdf', 'sdfgsd', '112asdf', '123sdf32fsd']

x = generate_startswith('dogcat')
y = generate_startswith('asdf')

xx = generate_matches('assault_traj_40_2')

z = DAG_minus(x, y)


print(x.match('dogcat'), x.match('asdf'))
print(y.match('dogcat'), y.match('asdf'))
print(z.match('dogcat'), z.match('asdf'))

#word_bank = positive_words + negative_words
print(word_bank)

S_plus = ['assault_10_schedule']
S_minus = ['prod_test', 'softmax_lr0.0001_4conv', 'product_column_test']

#from tokens import LOWERCASE, letters
#from learn_disjunctive_expr import match_sequence_contains, match_sequence_startswith, match_sequence_matches
#seq = [letters['c'], letters['a']]
#print('seq', match_sequence_matches('cat', seq))

#print('contains', match_sequence_contains('1234cat', seq))
#input('...')



# TODO why does StartsWith seem to always output a full sequence? Like
disj = learn_filter(S_plus, S_minus, generality_score, [pred_bindings['StartsWith'], pred_bindings['EndsWith'],
                                                        pred_bindings['Matches'], pred_bindings['Contains']])

for s in disj.sequences:
    print(s)

pos_words = [s for s in word_bank if disj.match(s)]
neg_words = [s for s in word_bank if not disj.match(s)]

print('Pos:', pos_words)
print('Neg:', neg_words)