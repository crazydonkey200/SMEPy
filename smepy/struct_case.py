import copy

class StructCase:
    """A case is a nugget containing entities and expressions."""
    def __init__(self, s_exp_w_list):
        self.entities = {}
        self.expressions = {}
        for s_exp_w in s_exp_w_list:
            s_exp, w = s_exp_w
            args = s_exp[1:]
            for arg in args:
                if not arg in self.entities:
                    ent = Entity(arg)
                    self.entities[ent.name] = ent
            exp = Expression(self, s_exp, w)
            self.expressions[exp.name] = exp
        self.vocab = current_vocab

    @property
    def expression_list(self):
        return [self.expressions[key] for key in list(self.expressions)]

    @property
    def entity_list(self):
        return [self.entities[key] for key in list(self.entites)]

    def __repr__(self):
        exps_str = '\n '.join([repr(self.expressions[key]) for key in list(self.expressions)])
        exps_str = '(' + exps_str + ')'
        ents_str = ', '.join([repr(self.entities[key]) for key in list(self.entities)])
        ents_str = '(' + ents_str + ')'        
        return '<' + exps_str + ',\n' + ents_str + '>'
            
class Expression:
    """Short for expression.
    A expression states a relation about some entities."""
    def __init__(self, case, s_exp, weight=1.0, create_new_pred=True, evidences=None):
        pred_name = s_exp[0]
        arg_list = s_exp[1:]
        num_of_args = len(arg_list)
        if pred_name in current_vocab:
            self.predicate = current_vocab[pred_name]
        elif create_new_pred:
            self.predicate = current_vocab.add(pred_name, num_of_args)
        else:
            print 'Unknown predicate', pred_name
            raise KeyError
        if current_vocab.check_arity(pred_name, num_of_args):
            self.args = [case.entities[arg] for arg in arg_list]
        self.weight = weight
        self.evidences = evidences
        self.case = case
    
    @property
    def name(self):
        s_exp_list = [arg.name for arg in self.args]
        s_exp_list.insert(0, self.predicate.name)
        return ' '.join(s_exp_list)

    def __repr__(self):
        return '<' + self.name + ', ' + repr(self.weight) + '>'

    def __deepcopy__(self, memo):
        new_copy = copy.copy(self)
        new_copy.evidences = copy.copy(self.evidences)
        return new_copy
    
class Entity: 
    """ """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<' + self.name + '>'

    
class Predicate:
    """Short for predicate."""
    def __init__(self, name, arity):
        self.name = name
        self.arity = arity

    def __repr__(self):
        return '<' + self.name + '>'
        
class Vocabulary:
    """Contains all the predicates."""
    def __init__(self):
        self.p_dict = {}

    def add(self, pred_name, arity):
        new_pred = Predicate(pred_name, arity)
        self.p_dict[pred_name] = new_pred
        return new_pred

    def __getitem__(self, pred_name):
        if not pred_name in self.p_dict:
            print 'Unknown predicate', pred_name
            raise KeyError
        else:
            return self.p_dict[pred_name]

    def __delitem__(self, pred_name):
        if not pred_name in self.p_dict:
            print 'Unknown predicate', pred_name
            raise KeyError
        else:
            del self.p_dict[pred_name]

    def __contains__(self, pred_name):
        return pred_name in self.p_dict
    
    def check_arity(self, pred_name, arity):
        if not pred_name in self.p_dict:
            print 'Unknown predicate', pred_name
            raise KeyError
        else:
            return self.p_dict[pred_name].arity == arity

    def __repr__(self):
        return '<' + repr(self.p_dict) + '>'

current_vocab = Vocabulary()
            
#test examples
v = Vocabulary()
v.add('r1', 2)
print v['r1'].name
# v['r2']
print v.check_arity('r1', 2)
print v.check_arity('r1', 1)

sc = StructCase([(['r1', 'e1', 'e2'], 2.0), (['r2', 'e1', 'e2'], 3.0)])
sc2 = copy.copy(sc)
sc3 = copy.deepcopy(sc)
print sc2.expressions == sc.expressions
print sc3.expressions == sc.expressions
print sc3.expressions['r1 e1 e2'].predicate == sc.expressions['r1 e1 e2'].predicate

water_flow = StructCase([(['greaterThan', 'bucket_1', 'bucket_2'], 2.0), (['flow', 'bucket_1', 'bucket_2', 'tube'], 3.0), (['greaterThan', 'bucket_2', 'bucket_1'], 2.0)])
heat_flow = StructCase([(['greaterThan', 'ball_1', 'ball_2'], 2.0), (['flow', 'ball_1', 'ball_2', 'stick'], 3.0)])
