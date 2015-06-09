# s-expression parse code from
# http://rosettacode.org/wiki/S-Expressions
import re
 
dbg = False
 
term_regex = r'''(?mx)
    \s*(?:
        (?P<brackl>\()|
        (?P<brackr>\))|
        (?P<num>\-?\d+\.\d+|\-?\d+)|
        (?P<sq>"[^"]*")|
        (?P<s>[^(^)\s]+)
       )'''
 
def parse_sexp(sexp):
    stack = []
    out = []
    if dbg: print("%-6s %-14s %-44s %-s" % tuple("term value out stack".split()))
    for termtypes in re.finditer(term_regex, sexp):
        term, value = [(t,v) for t,v in termtypes.groupdict().items() if v][0]
        if dbg: print("%-7s %-14s %-44r %-r" % (term, value, out, stack))
        if   term == 'brackl':
            stack.append(out)
            out = []
        elif term == 'brackr':
            assert stack, "Trouble with nesting of brackets"
            tmpout, out = out, stack.pop(-1)
            out.append(tmpout)
        elif term == 'num':
            v = float(value)
            if v.is_integer(): v = int(v)
            out.append(v)
        elif term == 'sq':
            out.append(value[1:-1])
        elif term == 's':
            out.append(value)
        else:
            raise NotImplementedError("Error: %r" % (term, value))
    assert not stack, "Trouble with nesting of brackets"
    return out[0]
 
def print_sexp(exp):
    out = ''
    if type(exp) == type([]):
        out += '(' + ' '.join(print_sexp(x) for x in exp) + ')'
    elif type(exp) == type('') and re.search(r'[\s()]', exp):
        out += '"%s"' % repr(exp)[1:-1].replace('"', '\"')
    else:
        out += '%s' % exp
    return out
 
 
# if __name__ == '__main__':
#     sexp = ''' ( ( data "quoted data" 123 4.5)
#          (data (123 (4.5) "(more" "data)")))'''
 
#     print('Input S-expression: %r' % (sexp, ))
#     parsed = parse_sexp(sexp)
#     print("\nParsed to Python:", parsed)
 
#     print("\nThen back to: '%s'" % print_sexp(parsed))

def read_s_exp_file(f_name):
    with open(f_name) as fl:
        fl_str = fl.read()
    return parse_sexp('(' + fl_str + ')')

def read_meld_file(f_name):
    s_exp_list = read_s_exp_file(f_name)
    mt_list = []
    if not (s_exp_list[0][0] == 'in-microtheory'):
        print 'Not a microtheory file!'
        raise IOError
    mt_name = s_exp_list[0][1]
    mt_facts = s_exp_list[1:]
    return (mt_name, mt_facts)
