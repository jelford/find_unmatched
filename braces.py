#! /usr/bin/env python

""" Tool for checking for unmatched open/close braces in files.
    But surely any half-decent IDE or compiler would do that for you?
    Surely. But sometimes LaTeX has some trouble, especially when it
    has to pass through an \input{...}.

    >>> print_list('test', 
    ...     condense_to_list(
    ...         check_file(
    ...             ['$ unmatched math', 
    ...             '\overline{ unmatched close', 
    ...             '(and also unmatched normal bracket',
    ...              'for good measure'], 
    ...             list_to_pairs(latex_symbol_list))))
    test - [1:1] ($)
    test - [2:10] ({)
    test - [3:1] (()
"""

import functools, operator

latex_symbol_list = ['{', '}', '$', '$', '(', ')']

def print_list(filename, errors):
    """ Just prints out the list of errors:
        
        >>> print_list('hello', [(')', 1, 3), ('(', 2, 4), ('{', 5, 10)])
        hello - [1:3] ())
        hello - [2:4] (()
        hello - [5:10] ({)
    """
    for message, line, column in errors:
        print('{filename} - [{line}:{column}] ({message})'.format(**locals()))

def check_file(f, open_close_pairs):
    """ Takes an iterable of lines, and returns a tuple containing a stack of
        unmatched {s and unmatched }s
        
        >>> check_file(['hello','worl{d','My {','name is Jim}', '{', '}'], {('{', '}')})
        {('{', '}'): ([(2, 5)], [])}
        >>> check_file(['} what','is this {'], {('{', '}')})
        {('{', '}'): ([(2, 9)], [(1, 1)])}
        >>> check_file(['} ] [ {'], {('{', '}'), ('[', ']')})
        {('[', ']'): ([(1, 5)], [(1, 3)]), ('{', '}'): ([(1, 7)], [(1, 1)])}

        >>> # If open/close are the same, then all are listed as "open"
        >>> check_file(['$latex math$', '$is harder'], {('$', '$')})
        {('$', '$'): ([(2, 1)], [])}
        >>> check_file(['$impossible to', 'know whether', '$unmatched open', '$or just multi-line'], {('$', '$')})
        {('$', '$'): ([(4, 1)], [])}

    """

    opens = {}
    closes = {}
    open_for = {}
    for open_symbol, close_symbol in open_close_pairs:
        opens[open_symbol] = []
        open_for[close_symbol] = opens[open_symbol]
        closes[close_symbol] = []

    line_number = 0
    for line in f:
        line_number += 1
        column = 0
        for sym in line:
            column += 1
            if sym in opens and open_for.get(sym, None) == opens[sym]:
                if len(opens[sym]) == 0:
                    opens[sym].append((line_number, column))
                else:
                    opens[sym].pop()
            elif sym in opens:
                opens[sym].append((line_number, column))
            elif sym in closes:
                if len(open_for[sym]) > 0:
                    open_for[sym].pop()
                else:
                    closes[sym].append((line_number, column))

    return { (o, c) : (opens[o], closes[c]) for o, c in open_close_pairs }

def list_to_pairs(l):
    """ Take an ordered list and return a set of pairs

        >>> list_to_pairs([1, 2, 3, 4])
        set([(1, 2), (3, 4)])

        >>> list_to_pairs(['a', 'b', 'c', 'd'])
        set([('a', 'b'), ('c', 'd')])
    """
    return {(l[2*i], l[2*i+1]) for i in range(len(l)/2)}

def condense_to_list(hit_dictionary):
    """ Take a (open, close) -> (unmatched_opens_list, unmatched_closes_list) and return an ordered list of all entries
    
        >>> condense_to_list({ ('{', '}') : ([(1,2), (3,4)], [(2,3), (4,5)]), ('[', ']') : ([(1,3), (3,3)], [(2,1), (4,6)]) })
        [('{', 1, 2), ('[', 1, 3), (']', 2, 1), ('}', 2, 3), ('[', 3, 3), ('{', 3, 4), ('}', 4, 5), (']', 4, 6)]
    """
    return sorted(functools.reduce(operator.add, 
                                [ 
                                    [(open_symbol, line, col) for line, col in opens] + [(close_symbol, line, col) for line, col in closes] 
                                        for ((open_symbol, close_symbol), (opens, closes)) in zip(hit_dictionary.keys(), hit_dictionary.values())
                                ] 
                ),
            key = lambda n : n[1:])

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Find unmatched curly braces")
    parser.add_argument('filenames', nargs='+', help='Files to check')
    parser.add_argument('--verbose', '-v', action='store_const', dest='verbose', const=True, help='Chat more')
    parser.add_argument('--symbols', nargs='*', action='store', dest='symbols', help='Bracket symbol to check for (overrides other flags)', default=['{', '}'])
    parser.add_argument('--latex', action='store_const', dest='symbols', const=latex_symbol_list, help="Check for LaTeX brackets (overrides other flags): { } [ ]")
    args = parser.parse_args()
    number_of_symbols = len(args.symbols)
    if number_of_symbols > 0 and number_of_symbols % 2 == 0:
        if args.verbose:
            print("Checking for: {brackets}".format(brackets = functools.reduce(lambda x, y: '{x} {y}'.format(x=x, y=y), args.symbols)))
        open_close_pairs = list_to_pairs(args.symbols)
        for filename in args.filenames:
            try:
                with open(filename, 'r') as to_check:
                    hits = check_file(to_check, open_close_pairs)
                    print_list(filename, condense_to_list(hits))
            except IOError:
                pass
    else:
        import sys
        sys.stderr.write("Must specify bracket symbols as a list of pairs, e.g. {program_name} {{ }} ( )\n".format(program_name = sys.argv[0]))
        sys.stderr.write("I read:\n")
        for sym in args.symbols:
            sys.stderr.write('{sym} '.format(sym=sym))
        sys.stderr.write('\n')
