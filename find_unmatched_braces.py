#! /usr/bin/env python

import functools, operator

def print_list(filename, errors):
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
    """

    opens = {}
    closes = {}
    open_for = {}
    for open_symbol, close_symbol in open_close_pairs:
        open_for[close_symbol] = open_symbol
        opens[open_symbol] = []
        closes[close_symbol] = []

    line_number = 0
    for line in f:
        line_number += 1
        column = 0
        for sym in line:
            column += 1
            if sym in opens:
                opens[sym].append((line_number, column))
            elif sym in closes:
                if len(opens[open_for[sym]]) > 0:
                    opens[open_for[sym]].pop()
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
    parser.add_argument('--symbols', nargs='*', help='Bracket symbol to check for', default=['{', '}'])
    args = parser.parse_args()
    if len(args.symbols) % 2 == 0:
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
        print("Must specify bracket symbols as a pair, e.g. {program_name} {{ }} ( )".format(program_name = sys.argv[0]))
