import numpy as np
import re
from tokens import *
from enum import Enum
from typing import Set, List, Tuple, Optional

class FIDEX_token(object):

    def __init__(self, token_symbol : str):
        self.token_symbol = token_symbol

    def match(self, s : str) -> bool:
        res = self.prefix_split_match(s)
        return (res is not None) and res[1] == ''

    def prefix_split_match(self, s : str) -> Optional[Tuple[str, str]]:
        raise NotImplemented

    def __str__(self):
        return f'<{self.token_symbol}>'

    def __repr__(self):
        return f'<{self.token_symbol}>'

class GeneralToken(FIDEX_token):

    def __init__(self, token_symbol : str, match_rule : str):
        super().__init__(token_symbol)
        self.match_rule = match_rule

    def prefix_split_match(self, s : str) -> Optional[Tuple[str, str]]:
        if len(s) == 0:
            return None
        match = re.match(r'^' + self.match_rule + r'$', s[0])
        if match:
            return (s[0], s[1:])
        else:
            return None


class ConstantToken(GeneralToken):

    def __init__(self, token_symbol : str):
        super().__init__(token_symbol, token_symbol)

class SequenceToken(FIDEX_token):

    def __init__(self, token_symbol : str, match_rule : str):
        super().__init__(token_symbol)
        self.match_rule = match_rule

    def prefix_split_match(self, s : str) -> Optional[Tuple[str, str]]:
        if len(s) == 0:
            return None
        re_string = f'^({self.match_rule}+)([\s\S]*)?$'
        match = re.match(re_string, s)
        if match is None:
            return None
        else:
            match_string = match.groups()[0]
            rest_string = match.groups()[1]
            return (match_string, rest_string)

tokens : List[FIDEX_token] = []

rank0_tokens = []
rank1_tokens = []
rank2_tokens = []
rank3_tokens = []
rank4_tokens = []

rank0_tokens += [ConstantToken(letter) for letter in 'abcdefghijklmnopqrstuvwxyz']
letters = {letter : token for letter, token in zip('abcdefghijklmnopqrstuvwxyz',rank0_tokens)}

rank0_tokens += [ConstantToken(letter) for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
rank0_tokens += [ConstantToken(number) for number in '0123456789']
rank0_tokens += [GeneralToken('-', '\-'),
           GeneralToken('_', '\_'),
           GeneralToken('.', '\.'),
           GeneralToken(';', '\;'),
           GeneralToken(':', '\:'),
           GeneralToken('[', '\['),
           GeneralToken(']', '\]'),
           GeneralToken('(', '\('),
           GeneralToken(')', '\)'),
           GeneralToken('/', '\/'),
           GeneralToken('\\', '\\\\'),
           GeneralToken(' ', '\s')]

rank1_tokens += [GeneralToken('UPPERCASE', '[A-Z]'),
           GeneralToken('LOWERCASE', '[a-z]'),
           GeneralToken('ALPHA', '[A-Za-z]'),
           GeneralToken('DIGIT', '\d')]

LOWERCASE = rank1_tokens[1]


rank2_tokens += [GeneralToken('ALPHANUMERIC', '[a-zA-Z\d]')]

rank3_tokens += [SequenceToken('UPPERCASE_SEQ', '[A-Z]'),
          SequenceToken('LOWERCASE_SEQ', '[a-z]'),
          SequenceToken('ALPHA_SEQ', '[A-Za-z]'),
          SequenceToken('DIGIT_SEQ', '\d')
         ]

rank4_tokens += [SequenceToken('ALPHANUMERIC_SEQ', '[a-zA-Z\d]')]


rank0_set = set(rank0_tokens)
rank1_set = set(rank1_tokens)
rank2_set = set(rank2_tokens)
rank3_set = set(rank3_tokens)
rank4_set = set(rank4_tokens)

def generality_score(t : FIDEX_token) -> float:
    if t in rank0_set:
        return 1
    elif t in rank1_set:
        return 2
    elif t in rank2_set:
        return 3
    elif t in rank3_set:
        return 4
    elif t in rank4_set:
        return 5
    else:
        raise Exception(f'unranked token {t}')

tokens = rank0_tokens + rank1_tokens + rank3_tokens + rank2_tokens + rank4_tokens

