instances = [
    (['cat', 'cats'],
     ['dog', '123', 'goat', 'CAT']), # starts with cat.

    (['0012', '0021', '1234'],
     ['saufbgaosd', 'AODFI', '00000']), # 4 digit number

    (['000', '00', '0', '00000'],
     ['adofioi23', '2oi3jdsf', 'o3qweajfisj']), # sequence of zeros.

    (['dogcat', 'catcat', '1234cat'],
     ['001234', 'asdf', 'asdfsdf', 'asdf2fe', 'asdfasdf']), # endswith cat

    (['cat1', 'cat2', 'cat3', 'cat4'],
     ['dog1', 'dog2', 'dog3', 'dog4']), # cats not dogs

    (['Robert M. Smith', 'John E. Doe', 'James F. Franco', 'Wesley W. Weimer'],
     ['John Stuart', 'Jimmy Mcgill', 'Johnny Walker', 'Jeffrey Dahmer']), # middle names

    #([])

]

