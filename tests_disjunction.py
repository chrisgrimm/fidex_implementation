from learn_disjunctive_expr import learn_filter, Disjunction
from tokens import FIDEX_token
from tokens import generality_score

#word_bank = ['Cat123', 'CatABC', 'Cat423', 'Cat222', 'CatCDE', 'CatEHA', 'Cat132']
word_bank = ['CatDogCat', 'CaDogCat', 'ArgleDogBarg', '12432', '1023432', 'BirdCart',
             'DogDog', 'BirdCat', 'Dog', 'Doggy', 'CatCat', '1234', 'Dogo', 'Cat']

S_plus = ['CatDogCat', 'DogDog', 'Dog']
S_minus = ['12432', 'BirdCart']

disj = learn_filter(S_plus, S_minus, generality_score)

pos_words = [s for s in word_bank if disj.match(s)]
neg_words = [s for s in word_bank if not disj.match(s)]

print('Pos:', pos_words)
print('Neg:', neg_words)
