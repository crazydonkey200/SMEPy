import struct_case as sc
import copy
import reader

class SME:
    """The main class that holds all
    the information of a structure mapping process."""
    def __init__(self, base, target):
        self.base = base
        self.target = target

    def match(self):
        matches = create_all_possible_matches(self.base, self.target)
        #print matches
        connect_matches(matches)
        valid_matches = consistency_propagation(matches)
        #print valid_matches
        structural_evaluation(valid_matches)
        kernel_mappings = find_kernel_mappings(valid_matches)
        #for km in kernel_mappings:
        #    print km
        #    print
        global_mappings = greedy_merge(kernel_mappings)
        return global_mappings

class Mapping:
    """ """
    def __init__(self, matches=None):
        self.base_to_target = {}
        self.target_to_base = {}
        self.matches = set()
        self.score = 0.0
        if matches:
            self.add_all(matches)

    def get_mapped_base(self, base):
        if base in self.base_to_target:
            return self.base_to_target[base]
        else:
            return None

    def get_mapped_target(self, target):
        if target in self.target_to_base:
            return self.target_to_base[target]
        else:
            return None

    def is_consistent_with(self, match):
        base = match.base
        target = match.target
        corresponding_target = self.get_mapped_base(base)
        corresponding_base = self.get_mapped_target(target)
        is_base_consistent = (not corresponding_target) or \
            (corresponding_target == target)
        is_target_consistent = (not corresponding_base) or \
            (corresponding_base == base)
        return is_base_consistent and is_target_consistent
        
    def mutual_consistent(self, mapping):
        for match in mapping.matches:
            if not self.is_consistent_with(match):
                #print 'Mapping is not consistent with', match
                return False
        return True 
    
    def add(self, match, check_consistency=True):
        if match in self.matches:
            return 
        elif (not check_consistency) or self.is_consistent_with(match):
            base = match.base
            target = match.target
            self.base_to_target[base] = target
            self.target_to_base[target] = base
            self.matches.add(match)
        else:
            print 'Mapping is not consistent with', match
            raise ValueError

    def add_all(self, matches, check_consistency=True):
        for match in matches:
            self.add(match, check_consistency)

    def merge(self, mapping):
        # consistency should be checked before merging
        self.add_all(mapping.matches, check_consistency=False) 

    def evaluate(self):
        self.score = 0.0
        for match in self.matches:
            self.score += match.score
        return self.score

    def copy(self):
        new_mapping = Mapping(self.matches)
        new_mapping.score = self.score
        return new_mapping

    def __str__(self):
        entity_matches = []
        expression_matches = []
        for match in self.matches:
            if isinstance(match.base, sc.Expression):
                expression_matches.append(match)
            elif isinstance(match.base, sc.Entity):
                entity_matches.append(match)
        expression_matches_str = \
            ',\n'.join(map(repr, expression_matches))
        entity_matches_str = ', '.join(map(repr, entity_matches))
        return 'expression mappings:\n' + expression_matches_str + \
            '\n' + 'entity mappings:\n' + entity_matches_str    
        
class Match:
    """ """
    def __init__(self, base, target, score=0.0):
        self.base = base
        self.target = target
        self.score = score
        self.children = []
        self.parents = []
        self.mapping = None
        self.is_incomplete = False
        self.is_inconsistent = False
        
    def add_parent(self, parent):
        self.parents.append(parent)

    def add_child(self, child):
        self.children.append(child)
        
    def local_evaluation(self):
        if isinstance(self.base, sc.Expression):
            self.score = predicate_match_score(self.base.predicate,
                                               self.target.predicate)
        else:
            self.score = 0.0
        return self.score
        
    def __repr__(self):
        return '('+repr(self.base)+' -- '+repr(self.target)+')'        

    def __eq__(self, other):
        return isinstance(other, Match) and\
            (self.base == other.base) and \
            (self.target == other.target)

    def __hash__(self):
        return hash(repr(self))

    
class Params:
    """ """
    pass

def predicate_match_score(pred_1, pred_2):
    if pred_1.predicate_type == 'relation':
        if pred_1.name == pred_2.name:
            return 0.005
    elif pred_1.predicate_type == 'function':
        return 0.002
    else:
        return 0.0

def are_predicates_matchable(pred_1, pred_2):
    if pred_1.predicate_type != pred_2.predicate_type:
        return False
    elif pred_1.predicate_type == 'relation':
        return pred_1.name == pred_2.name
    else:
        return True

def are_matchable(item_1, item_2):
    is_exp_1 = isinstance(item_1, sc.Expression)
    is_exp_2 = isinstance(item_2, sc.Expression)
    if is_exp_1 and is_exp_2:
        return are_predicates_matchable(item_1.predicate,
                                        item_2.predicate)
    elif (not is_exp_1) and (not is_exp_2):
        return True
    else:
        return False
    
# need to change the pair stuff into match stuff
def create_all_possible_matches(case_1, case_2):
    exp_list_1 = case_1.expression_list
    exp_list_2 = case_2.expression_list
    matches = set()
    for exp_1 in exp_list_1:
        for exp_2 in exp_list_2:
            new_matches = match_expression(exp_1, exp_2)
            matches = set.union(matches, new_matches)
    return list(matches)
    
def match_expression(exp_1, exp_2):
    pred_1 = exp_1.predicate
    pred_2 = exp_2.predicate
    args_1 = exp_1.args
    args_2 = exp_2.args
    pair_list = [(exp_1, exp_2)] + zip(args_1, args_2)
    if all([are_matchable(pair[0], pair[1]) for pair in pair_list]):
        match_list = [Match(pair[0], pair[1]) for pair in pair_list]
        return set(match_list)
    else:
        return set()

def connect_matches(matches):
    match_dict = {}
    for match in matches:
        match_dict[(match.base, match.target)] = match
    for match in matches:
        base = match.base
        target = match.target
        if isinstance(base, sc.Expression):
            arg_pair_list = zip(base.args, target.args)
            for arg_pair in arg_pair_list:
                if arg_pair in match_dict:
                    child_match = match_dict[arg_pair]
                    child_match.add_parent(match)
                    match.add_child(child_match)
                else:
                    match.is_incomplete = True

def consistency_propagation(matches):
    match_graph = dict([(match, match.children) for match in matches])
    ordered_from_leaves_matches = topological_sort(match_graph)
    
    for match in ordered_from_leaves_matches:
        match.mapping = Mapping([match])
        for child in match.children:
            if match.mapping.mutual_consistent(child.mapping):
                match.mapping.merge(child.mapping)
            else:
                match.is_inconsistent = True
                break
    valid_matches = [match for match in matches \
                     if (not (match.is_incomplete or
                              match.is_inconsistent))]
    return valid_matches

def structural_evaluation(matches, trickle_down_factor=16):
    #assume matches are still topologically sorted,
    #otherwise should sort it first
    for match in matches:
        match.local_evaluation()
    ordered_from_root_matches = matches[::-1]

    for match in ordered_from_root_matches:
        for child in match.children:
            child.score += match.score * trickle_down_factor
            if child.score > 1.0:
                child.score = 1.0
    
    for match in ordered_from_root_matches:
        match.mapping.evaluate()

    return matches

def find_kernel_mappings(valid_matches):
    root_matches = []
    for match in valid_matches:
        are_parents_valid = [not (parent in valid_matches) \
                             for parent in match.parents]
        if all(are_parents_valid):
            root_matches.append(match)
    return [match.mapping.copy() for match in root_matches]

def greedy_merge(kernel_mappings):
    sorted_k_mapping_list = sorted(kernel_mappings,
                                   key=(lambda mapping: mapping.score),
                                   reverse=True)
    global_mappings = []
    max_score = 0.0
    while (len(global_mappings) < 3) and \
          (len(sorted_k_mapping_list) > 0):
        global_mapping = sorted_k_mapping_list[0]
        sorted_k_mapping_list.remove(global_mapping)
        
        for kernel_mapping in sorted_k_mapping_list[:]:
            if global_mapping.mutual_consistent(kernel_mapping):
                global_mapping.merge(kernel_mapping)
                sorted_k_mapping_list.remove(kernel_mapping)
        
        score = global_mapping.evaluate()
        if score <= 0.8 * max_score:
            break
        elif score > max_score:
            max_score = score
        global_mappings.append(global_mapping)
    
    global_mappings.sort(key=lambda mapping: mapping.score, \
                         reverse=True)
    return global_mappings

def topological_sort(graph_dict):
    """Input: graph represented as
    {node: [next_node_1, next_nodet_2], ...}"""
    sorted_list = []
    sorted_set = set()
    new_graph_dict = graph_dict.copy()
    while new_graph_dict:
        for node in new_graph_dict:
            next_node_list = new_graph_dict[node]
            if all([(next_node in sorted_set) \
                    for next_node in next_node_list]):
                sorted_list.append(node)
                sorted_set.add(node)
                del new_graph_dict[node]
                break
        else:
            print 'Cyclic graph!'
            return
    return sorted_list    
