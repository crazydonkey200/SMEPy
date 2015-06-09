import copy

def get_hash_name(item):
    if isinstance(item, list):
        return '(' + ' '.join(map(get_hash_name, item)) + ')'
    else:
        return item

class StructCase:
    """A case is a nugget containing entities and expressions."""
    def __init__(self, s_exp_w_list):
        self.items = {}
        for s_exp_w in s_exp_w_list:
            self.add_s_exp_w(s_exp_w)
        self.vocab = current_vocab
    
    @property
    def expression_list(self):
        return [self.items[key] \
                for key in list(self.items) \
                if isinstance(self.items[key], Expression)]

    @property
    def entity_list(self):
        return [self.items[key] \
                for key in list(self.items) \
                if isinstance(self.items[key], Entity)]

    @property
    def item_list(self):
        return [self.items[key] for key in list(self.items)]

    def __getitem__(self, index):
        new_index = index
        if isinstance(index, list):
            new_index = get_hash_name(index)
        if new_index in self:
            return self.items[new_index]
        else:
            return None
    
    def add(self, item):
        if not item in self:
            if isinstance(item, list):
                return self.add_s_exp_w((item, 1.0))
            elif isinstance(item, tuple):
                return self.add_s_exp_w(item)
            elif isinstance(item, str):
                return self.add_entity(Entity(item))
            elif isinstance(item, Expression):
                return self.add_expression(item)
            elif isinstance(item, Entity):
                return self.add_entity(item)
        elif isinstance(item, Expression) or isinstance(item, Entity):
            return item
        else:
            return self[item]

    def add_s_exp_w(self, s_exp_w):
        s_exp, w = s_exp_w
        new_expression = Expression(self, s_exp, w)
        self.items[new_expression.name] = new_expression
        return new_expression

    def add_entity(self, entity):
        self.items[entity.name] = entity
        return entity

    def add_expression(self, expression):
        self.items[expression.name] = expression
        for arg in expression.args:
            self.add(arg)
        return expression
        
    def __contains__(self, item):
        if isinstance(item, Expression) or \
           isinstance(item, Entity):
            return item.name in self.items
        elif isinstance(item, list):
            return get_hash_name(item) in self.items
        else:
            return item in self.items

    def __deepcopy__(self, memo):
        return StructCase([(expression.list_form, expression.weight) \
                           for expression in self.expression_list])
        
    def __str__(self):
        exps_str = '\n '.join([repr(expression) \
                               for expression in self.expression_list])
        exps_str = '(' + exps_str + ')'
        ents_str = ', '.join([repr(entity) \
                              for entity in self.entity_list])
        ents_str = '(' + ents_str + ')'        
        return '<' + exps_str + ',\n' + ents_str + '>'
            
class Expression:
    """Short for expression.
    A expression states a relation about some entities."""
    def __init__(self, case, s_exp, weight=1.0, create_new_pred=True, \
                 evidences=None):
        pred_name = s_exp[0]
        arg_list = s_exp[1:]
        num_of_args = len(arg_list)
        self.args = []
        if pred_name in current_vocab:
            self.predicate = current_vocab[pred_name]
        elif create_new_pred:
            self.predicate = current_vocab.add(pred_name, num_of_args)
        else:
            print 'Unknown predicate', pred_name
            raise KeyError
        if current_vocab.check_arity(pred_name, num_of_args):
            for arg in arg_list:
                self.args.append(case.add(arg))
        self.weight = weight
        self.evidences = evidences
        self.case = case
    
    @property
    def name(self):
        s_exp_list = [arg.name for arg in self.args]
        s_exp_list.insert(0, self.predicate.name)
        return '(' + ' '.join(s_exp_list) + ')'

    @property
    def list_form(self):
        return [self.predicate.list_form] + \
            [arg.list_form for arg in self.args]
    
    def __repr__(self):
        return '<' + self.name + ', ' + repr(self.weight) + '>'

    # def __hash__(self):
    #     return hash(self.name)
        
    def __deepcopy__(self, memo):
        new_copy = copy.copy(self)
        new_copy.evidences = copy.copy(self.evidences)
        return new_copy
    
class Entity: 
    """ """
    def __init__(self, name):
        self.name = name

    @property
    def list_form(self):
        return self.name

    # def __hash__(self):
    #     return hash(self.name)

    def __repr__(self):
        return '<' + self.name + '>'
    
class Predicate:
    """Short for predicate."""
    def __init__(self, name, arity):
        self.name = name
        self.arity = arity

    @property
    def list_form(self):
        return self.name
        
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

class Test:
    def __init__(self, i):
        self.i = i

    def __hash__(self):
        return hash(self.i)

t = Test(1)
d = {t: 2}

v = Vocabulary()
v.add('r1', 2)
print v['r1'].name
# v['r2']
print v.check_arity('r1', 2)
print v.check_arity('r1', 1)

sc = StructCase([(['r1', 'e1', 'e2'], 2.0),
                 (['r2', 'e1', 'e2'], 3.0)])
sc2 = copy.copy(sc)
sc3 = copy.deepcopy(sc)
print sc3
print sc3.items
print sc2.items == sc.items
print sc3.items == sc.items
print sc3['(r1 e1 e2)'].predicate == sc['(r1 e1 e2)'].predicate

water_flow = StructCase( \
    [(['greaterThan', 'bucket_1', 'bucket_2'], 2.0), \
     (['flow', 'bucket_1', 'bucket_2', 'tube'], 3.0), \
     (['greaterThan', 'bucket_2', 'bucket_1'], 2.0), \
     (['cause', \
       ['greaterThan', 'bucket_1', 'bucket_2'], \
       ['flow', 'bucket_1', 'bucket_2', 'tube']], 1.0), \
     (['cause', \
       ['greaterThan', 'bucket_2', 'bucket_1'], \
       ['flow', 'bucket_1', 'bucket_2', 'tube']], 1.0)])

heat_flow = StructCase(
    [(['greaterThan', 'ball_1', 'ball_2'], 2.0), \
     (['flow', 'ball_1', 'ball_2', 'stick'], 3.0), \
     (['cause', \
       ['greaterThan', 'ball_1', 'ball_2'], \
       ['flow', 'ball_1', 'ball_2', 'stick']], 1.0)])
     # (['cause', \
     #   ['greaterThan', 'ball_2', 'ball_1'], \
     #   ['flow', 'ball_1', 'ball_2', 'stick']], 1.0)])

