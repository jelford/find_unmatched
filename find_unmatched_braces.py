#! /usr/bin/env python

def print_list(filename, errors):
    for message, line, column in errors:
        print('{filename} - [{line}:{column}] ({message})'.format(**locals()))

def check_file(f):
    """ Takes an iterable of lines, and returns a tuple containing a stack of
        unmatched {s and unmatched }s
        
        >>> check_file(['hello','worl{d','My {','name is Jim}'])
        ([(2, 5)], [])
        >>> check_file(['} what','is this {'])
        ([(2, 9)], [(1, 1)])
    """
    opens = []
    closes = []
    line_number = 0
    for line in f:
        line_number += 1
        column = 0
        for col in line:
            column += 1
            if col == '{':
                opens.append((line_number, column))
            elif col == '}':
                if len(opens) > 0:
                    opens.pop()
                else:
                    closes.append((line_number, column))

    return opens, closes

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Find unmatched curly braces")
    parser.add_argument('filenames', nargs='+', help='Files to check')
    args = parser.parse_args()
    for filename in args.filenames:
        try:
            with open(filename, 'r') as to_check:
                opens, closes = check_file(to_check)
                
                print_list(filename,
                    sorted([('{', line, col) for line, col in opens] + 
                            [('}', line, col) for line, col in closes],
                        key=lambda n : n[:1]))
        except IOError:
            pass
