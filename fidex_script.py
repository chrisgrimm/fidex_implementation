import os, sys, argparse, signal
from learn_disjunctive_expr import learn_filter, pred_bindings
from tokens import generality_score

parser = argparse.ArgumentParser()
parser.add_argument('words', type=str, nargs='+')
args = parser.parse_args()


def format_line(left_word, right_word):
    max_len = 30
    to_str_right = lambda word_opt: '' if word_opt is None else ('%s [%s]' % (word_opt[1][:max_len], word_opt[0]))
    to_str_left = lambda word_opt: '' if word_opt is None else ('[%s] %s' % (word_opt[0], word_opt[1][:max_len]))
    line = ("+{:<%s} -{:>%s}" % (max_len+10, max_len+10)).format(to_str_left(left_word), to_str_right(right_word))
    #line = f'{"+"+to_str_left(left_word):<{max_len+10}} {to_str_right(right_word)+"-":>{max_len+10}}'
    return line

def format_words(positive_words, negative_words):
    lines = []
    for i in range(max(len(positive_words), len(negative_words))):
        pos_word = positive_words[i] if i < len(positive_words) else None
        neg_word = negative_words[i] if i < len(negative_words) else None
        lines.append(format_line(pos_word, neg_word))
    return '\n'.join(lines[::-1])


def interactive_loop():
    words = list(enumerate(args.words[:]))
    word_dict = dict(words)
    S_plus = []
    S_minus = []
    plus_filtered = []
    minus_filtered = words[:]
    token_seq = []
    #print(format_words([], words))
    D_tilde, D_tilde_minus = [], []
    while True:
        try:
            print(format_words(plus_filtered, minus_filtered))
            inp = input('> ')
            i = int(inp)
            word = word_dict[i]
        except EOFError:
            #print(token_seq)
            break
        except ValueError:
            print('input must be an integer!')
            continue
        except KeyError:
            print('[%s] does not match a word.' % i)
            continue
        # if the word is listed as filtered out
        if word in [w for i, w in minus_filtered]:
            if word in S_minus:
                S_minus.remove(word)
            if word not in S_plus:
                S_plus.append(word)

        if word in [w for i, w in plus_filtered]:
            if word in S_plus:
                S_plus.remove(word)
            if word not in S_minus:
                S_minus.append(word)
        pred_name, disj = learn_filter(
            S_plus,
            S_minus,
            generality_score,
            [pred_bindings['StartsWith'], pred_bindings['EndsWith'], pred_bindings['Matches'], pred_bindings['Contains']])
        plus_filtered, minus_filtered = [], []
        for i, w in words:
            if disj.match(w):
                plus_filtered.append((i,w))
            else:
                minus_filtered.append((i,w))



if __name__ == '__main__':
    interactive_loop()


