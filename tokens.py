import numpy as np
import re
from tokens import *
from enum import Enum
from typing import Set, List, Tuple, Optional

class FIDEX_token(object):

    def __init__(self, token_symbol : str):
        self.token_symbol = token_symbol

    def match(self, s : str) -> bool:
        split = self.split_match(s)
        return split is not None

    def split_match(self, s : str) -> Optional[Tuple[str, str]]:
        raise NotImplemented

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

    def split_match(self, s : str) -> Optional[Tuple[str, str]]:
        if len(s) == 0:
            return None
        match = re.match(r'^'+self.match_rule+r'$', s)
        if match:
            return (s[0], '')
        else:
            return None

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

    def split_match(self, s : str) -> Optional[Tuple[str, str]]:
        if len(s) == 0:
            return None
        re_string = f'^({self.match_rule}+)$'
        match = re.match(re_string, s)
        if match is None:
            return None
        else:
            match_string = match.groups()[0]
            rest_string = s[len(match_string):]
            return (match_string, rest_string)

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

tokens += [ConstantToken(letter) for letter in 'abcdefghijklmnopqrstuvwxyz']
letters = {letter : token for letter, token in zip('abcdefghijklmnopqrstuvwxyz',tokens)}
tokens += [ConstantToken(letter) for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
tokens += [ConstantToken(number) for number in '0123456789']
tokens += [GeneralToken('-', '\-'),
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
tokens += [GeneralToken('UPPERCASE', '[A-Z]'),
           GeneralToken('LOWERCASE', '[a-z]'),
           GeneralToken('ALPHA', '[A-Za-z]'),
           GeneralToken('DIGIT', '\d')
          ]
           #GeneralToken('ALPHANUMERIC', '[a-zA-Z\d]')]
#tokens += [SequenceToken('UPPERCASE_SEQ', '[A-Z]'),
#           SequenceToken('LOWERCASE_SEQ', '[a-z]'),
#           SequenceToken('ALPHA_SEQ', '[A-Za-z]'),
#           SequenceToken('DIGIT_SEQ', '\d')
#          ]
