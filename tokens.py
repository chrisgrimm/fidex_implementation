import numpy as np
import re
from tokens import *
from enum import Enum
from typing import Set, List, Tuple, Optional

class FIDEX_token(object):

    def __init__(self, token_symbol : str):
        self.token_symbol = token_symbol

    def match(self, s : str) -> bool:
        raise NotImplemented

    def __str__(self):
        return f'<{self.token_symbol}>'

class GeneralToken(FIDEX_token):

    def __init__(self, token_symbol : str, match_rule : str):
        super().__init__(token_symbol)
        self.match_rule = match_rule

    def match(self, s : str) -> bool:
        if len(s) == 0:
            return ('', '')
        match = re.match(r'^'+self.match_rule+r'$', s)
        return (match is not None)


class ConstantToken(GeneralToken):

    def __init__(self, token_symbol : str):
        super().__init__(token_symbol, token_symbol)

class SequenceToken(FIDEX_token):

    def __init__(self, token_symbol : str, match_rule : str):
        super().__init__(token_symbol)
        self.match_rule = match_rule

    def match(self, s : str) -> Tuple[str, str]:
        if len(s) == 0:
            return ('', '')
        re_string = f'^({self.match_rule}+)$'
        match = re.match(re_string, s)
        return (match is not None)

tokens : List[FIDEX_token] = []
tokens += [ConstantToken(letter) for letter in 'abcdefghijklmnopqrstuvwxyz']
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
           GeneralToken('DIGIT', '\d')]
tokens += [SequenceToken('UPPERCASE_SEQ', '[A-Z]'),
           SequenceToken('LOWERCASE_SEQ', '[a-z]'),
           SequenceToken('ALPHA_SEQ', '[A-Za-z]'),
           SequenceToken('DIGIT_SEQ', '\d')]
