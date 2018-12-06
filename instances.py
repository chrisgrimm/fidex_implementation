import os, re
from typing import List

class Instance(object):

    def __init__(self, all_words : List[str], regex : str):
        self.all_words = all_words
        self.regex = regex
        self.positive_words = [word for word in all_words if re.match(regex, word)]
        self.negative_words = [word for word in all_words if not re.match(regex, word)]

    def __repr__(self):
        return f'Instance({self.regex}, [{",".join(self.positive_words[:3])}, ...],  [{",".join(self.negative_words[:3])}, ...])'

    def __str_(self):
        return f'Instance({self.regex}, [{",".join(self.positive_words[:3])}, ...],  [{",".join(self.negative_words[:3])}, ...])'


instances = [
    Instance(['cat', 'cats', 'dog', '123', 'goat', 'CAT'], '^cat.*?$'), # startswith cat
    Instance(['0012', '0021', '1234', 'saufbgaosd', 'AODFI', '00000'], '^\d\d\d\d$'), # 4 digit number
    Instance(['000', '00', '0', '00000', 'adofioi23', '2oi3jdsf', 'o3qweajfisj'], '^0+?$'), # sequence of zeros
    Instance(['dogcat', 'catcat', '1234cat', '001234', 'asdf', 'asdfsdf', 'asdf2fe', 'asdfasdf'], '^.*?cat$'), # endswith cat
    Instance(['cat1', 'cat2', 'cat3', 'cat4', 'dog1', 'dog2', 'dog3', 'dog4'], '^cat.*?$'), # cats not dogs
    Instance(['Robert M. Smith', 'John E. Doe', 'James F. Franco', 'Wesley W. Weimer',
              'John Stuart', 'Jimmy Mcgill', 'Johnny Walker', 'Jeffrey Dahmer'], '^.*?\..*?$') # middle names
]


with open('ls_outputs.txt', 'r') as f:
    lines = f.readlines()
all_words = [line.split(' ') for line in lines]

instances += [
    Instance(all_words[0], '^.*?fidex.*?$'), # contains fidex
    Instance(all_words[0], '^.*?py$'), # endswith py
    Instance(all_words[0], '^.*?txt$'), # endswith txt
    Instance(all_words[0], '^test.*?$'), # startswith test

    Instance(all_words[1], '^.*?png$'), # ends with png
    Instance(all_words[1], '^venv.*?$'), # starts with venv
    Instance(all_words[1], '^Gradly.*?$'), # starts with gradly
    Instance(all_words[1], '^.*?\d+?.*?$'), # contains numbers
    Instance(all_words[1], '^.+?\d+?$'), # endswith numbers

    Instance(all_words[2], '^.*?samples.*?$'), # contains samples
    Instance(all_words[2], '^.*?image.*?$'), # contains image
    Instance(all_words[2], '^commence.*?$'), # startswith commence
    Instance(all_words[2], '^.*?sokoban.*?$'), # contains sokoban
    Instance(all_words[2], '^.*?png$'), # endswith png
    Instance(all_words[2], '^[A-Z].*?$'), # startswith uppercase
    Instance(all_words[2], '^.*?\d+?.*?$'), # contains number

    Instance(all_words[3], '^all.*?$'), # startswith all
    Instance(all_words[3], '^.*?sokoban.*?$'), # contains sokoban
    Instance(all_words[3], '^.*?pacman.*?$'), # contains pacman
    Instance(all_words[3], '^.*?assault.*?$'), # contains assault
    Instance(all_words[3], '^.*?py$'), # endswith py
    Instance(all_words[3], '^grab.*?$'), # startwith grab
    Instance(all_words[3], '^.*?png$'), # endswith png
    Instance(all_words[3], '^.*?dqn.*?$'), # contains dqn
    Instance(all_words[3], '^max\_image\d\.png$'), # matches max_image\d
    Instance(all_words[3], '^.*?\d.*?$'), # contains numbers
    Instance(all_words[3], '^.*?metacontroller.*?$'), # contains metacontroller

    Instance(all_words[4], '^assault.*?$'), # startswith assault
    Instance(all_words[4], '^.*?vis$'), #endswith vis
    Instance(all_words[4], '^.*?\d'), # endswith number
    Instance(all_words[4], '^assault\_traj\_40\_\d$'), # matches assault traj 40 run
    Instance(all_words[4], '^part\d.*?$'), # startswith part\d
    Instance(all_words[4], '^.*?sokoban.*?$'), #contains sokoban

    Instance(all_words[6], '^\d+x.*?$'), #startswith multiplier
    Instance(all_words[6], '^.*?resets$'), #endswith resets
    Instance(all_words[6], '^internal.*?$'), #startswith internal
    Instance(all_words[6], '^\D+?$'), # no digits
    Instance(all_words[6], '^.*?run.*?'), # contains run

    Instance(all_words[7], '^.*?py$'), # endswith py
    Instance(all_words[7], '^gan.*?$'), #startswith gan
]

if __name__ == '__main__':
    for i, instance in enumerate(instances):
        print(i, instance)






