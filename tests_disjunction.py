from learn_disjunctive_expr import learn_filter, Disjunction, pred_bindings
from tokens import FIDEX_token
from tokens import generality_score
from genDAG import generate_startswith, generate_endswith, generate_matches, generate_contains
from fidex_dag import DAG_minus, DAG_intersect

#word_bank = ['Cat123', 'CatABC', 'Cat423', 'Cat222', 'CatCDE', 'CatEHA', 'Cat132']
#word_bank = ['CatDogCat', 'CaDogCat', 'ArgleDogBarg', '12432', '1023432', 'BirdCart',
#             'DogDog', 'BirdCat', 'Dog', 'Doggy', 'CatCat', '1234', 'Dogo', 'Cat' ,'CatCatCatCatCat', 'CatCatCatCatCatCat', 'DogDogDog']

positive_words = ['cat1', 'cat2', 'cat3', 'cat4']
negative_words = ['dog1', 'dog2', 'dog3', 'dog4']

#positive_words = ['123cats456', 'cats', 'asdcats12312']
#negative_words = ['asdfsdf', 'sdfgsd', '112asdf', '123sdf32fsd']

x = generate_startswith('dogcat')
y = generate_startswith('asdf')

z = DAG_minus(x, y)


print(x.match('dogcat'), x.match('asdf'))
print(y.match('dogcat'), y.match('asdf'))
print(z.match('dogcat'), z.match('asdf'))

word_bank = positive_words + negative_words
print(word_bank)

S_plus = ['cat1']
S_minus = ['dog1']

from tokens import LOWERCASE, letters
from learn_disjunctive_expr import match_sequence_contains
seq = [LOWERCASE, LOWERCASE, letters['t']]

#print('contains', match_sequence_contains('1234cat', seq))
#input('...')


disj = learn_filter(S_plus, S_minus, generality_score, [pred_bindings['Matches']])

for s in disj.sequences:
    print(s)

pos_words = [s for s in word_bank if disj.match(s)]
neg_words = [s for s in word_bank if not disj.match(s)]

print('Pos:', pos_words)
print('Neg:', neg_words)