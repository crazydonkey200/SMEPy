#import struct_case as sc

class SME:
    """The main class that holds all
    the information of a structure mapping process."""
    pass

class Mapping:
    """ """
    pass
    
class Match:
    """ """
    def __init__(self, base, target, score=0.0):
        self.base = base
        self.target = target
        self.score = score
        self.children = []
        self.parents = []
        
    def __repr__(self):
        return '('+repr(self.base)+' -- '+repr(self.target)+')'        

    def __eq__(self, other):
        return isinstance(other, Match) and (self.base == other.base) and \
            (self.target == other.target)

    def __hash__(self):
        return hash(repr(self))
        
class Params:
    """ """
    pass

def predicate_similarity(pred_1, pred_2):
    if pred_1.name == pred_2.name:
        return 1.0
    else:
        return 0.0

def are_predicates_matchable(pred_1, pred_2):
    return pred_1.name == pred_2.name    

# need to change the pair stuff into match stuff
def create_all_possible_matches(case_1, case_2):
    exp_list_1 = case_1.expression_list
    exp_list_2 = case_2.expression_list
    pairs = set()
    for exp_1 in exp_list_1:
        for exp_2 in exp_list_2:
            new_pairs = pair_expression(exp_1, exp_2)
            pairs = set.union(pairs, new_pairs)
    return [Match(pair[0], pair[1]) for pair in pairs]
    
def pair_expression(exp_1, exp_2):
    pred_1 = exp_1.predicate
    pred_2 = exp_2.predicate
    args_1 = exp_1.args
    args_2 = exp_2.args
    if are_predicates_matchable(pred_1, pred_2):
        return set([(exp_1, exp_2)] + zip(args_1, args_2))
    else:
        return set()    
