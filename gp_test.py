# Benjamin Good
# 2021-07-16
# Test program for genetic programming

import math, random

DEPTH = 5
success_prob = 0.5
reward = 10

def unpack(arg):
	if type(arg) is tuple:
		return func_wrapper(arg)
	else:
		return arg
	
def unpack_args(arg1, arg2):
	a = arg1
	b = arg2
	if type(arg1) is tuple:
		#a = arg1[0](arg1[1], arg1[2])
		a = run(a)
	if type(arg2) is tuple:
		#b = arg2[0](arg2[1], arg2[2])
		b = run(b)
	return a, b

def func_wrapper(func):
	if len(func) == 3:
		return func[0](func[1], func[2])
	else:
		return func[0](func[1], func[2], func[3])

# cmp_vals is used at the root of individuals
# it is also used as an argument in ifelse functions
def cmp_vals(arg1, arg2, arg3):
	arg2 = run(arg2)
	arg3 = run(arg3)
	if arg1 == "<":
		return arg2 < arg3
	if arg1 == ">":
		return arg2 > arg3
	if arg1 == "==":
		return arg2 == arg3
	if arg1 == ">=":
		return arg2 >= arg3
	if arg1 == "<=":
		return arg2 <= arg3
	if arg1 == "!=":
		return arg2 != arg3

## Primitive definitions go here

def ifelse(arg1, arg2, arg3):
	if arg1[0](arg1[1], arg1[2], arg1[3]):
		return run(arg2)
	else:
		return run(arg3)

def int_value():
	return random.randrange(1000)

def double_value():
	return random.randrange(1000) * random.random()

def get_prob():
	return success_prob

def get_reward():
	return reward

def add(arg1, arg2):
	a, b = unpack_args(arg1, arg2)
	return a + b

def sub(arg1, arg2):
	a, b = unpack_args(arg1, arg2)
	return a - b

def mult(arg1, arg2):
	a, b = unpack_args(arg1, arg2)
	return a * b

def div(arg1, arg2):
	a, b = unpack_args(arg1, arg2)
	if b == 0:
		return 0
	return a / b

def comparison():
	cmp_ops = ["==", "<=", ">=", "<", ">"]
	return random.choice(cmp_ops)
	
## End of primitive definitions

term_set = [int_value, double_value, get_prob, get_reward]
func_set = [mult, div, add, sub, ifelse]

def gen_expr(func_set, term_set, method, max_depth, set_prob = 1, canend = True):
	# The root should be a comparison
	if max_depth == 5:
		arg1 = comparison()
		arg2 = gen_expr(func_set, term_set, method, max_depth-1, set_prob)
		arg3 = gen_expr(func_set, term_set, method, max_depth-1, set_prob)
		expr = (cmp_vals, arg1, arg2, arg3)
	elif canend and (random.random() < set_prob or max_depth < 1):
		# Choose from the terminal set, then call the selected function to obtain a value for the node.
		expr = random.choice(term_set)
		expr = expr()
	else:
		func = random.choice(func_set)
		# ifelse functions take 3 arguments, the first one being a cmp_vals function
		# Since ifelse's arguments are all supposed to be functions, canend is set to False for arg2 and arg3.
		if func.__name__ == "ifelse":
			e1 = gen_expr(func_set, term_set, method, max_depth-1, set_prob)
			e2 = gen_expr(func_set, term_set, method, max_depth-1, set_prob)
			arg1 = (cmp_vals, comparison(), e1, e2)
			arg2 = gen_expr(func_set, term_set, method, max_depth-1, set_prob, canend = False)
			arg3 = gen_expr(func_set, term_set, method, max_depth-1, set_prob, canend = False)
			expr = (func, arg1, arg2, arg3)
		else:
			arg1 = gen_expr(func_set, term_set, method, max_depth-1, set_prob)
			arg2 = gen_expr(func_set, term_set, method, max_depth-1, set_prob)
			expr = (func, arg1, arg2)
	return expr

def is_func(prim):
	if globals[str(prim)]:
		return True
	return False

def get_size(node, size=0):
	if type(node) is tuple:
		size = get_size(node[1], size)
		size = get_size(node[2], size)
	
	return size + 1

# Pick a node in a tree
# Could be used for recombination/mutation
def pick_node(node, prob):
	if random.random() < prob:
		return node
	
	if type(node) is tuple:
		node_arg1 = pick_node(node[1], 1/(get_size(node[1])))
		node_arg2 = pick_node(node[2], 1/(get_size(node[2])))
		if node_arg1 is not None and node_arg2 is not None:
			return random.choice([node_arg1, node_arg2])
		if node_arg1 is None:
			if node_arg2 is None:
				return None
			else:
				return node_arg2
		else:
			return node_arg1

# Takes two individuals as arguments
def recombination(node, other):
	new_node = None
	arg1 = None
	arg2 = None
	# Get subtree from other parent
	subtree = pick_node(other, 1/get_size(other))
	# Potentially use the subtree for copying genetic material to child, otherwise use first parent
	if random.random() < 1/get_size(node):
		node = subtree
	if type(node) is tuple:
		# Call the recombination function again if an argument is a function, otherwise just get terminal from tree
		if type(node[1]) is tuple:
			arg1 = recombination(node[1], other)
		else:
			arg1 = node[1]
			
		if type(node[2]) is tuple:
			arg2 = recombination(node[2], other)
		else:
			arg2 = node[2]
		new_node = (node[0], arg1, arg2)
	else:
		new_node = node
	
	return new_node

# Alternative recombination algorithm
def recombination_alt(node, st, prob, co=True):
	new_node = None
	arg1 = None
	arg2 = None
	res = co
	
	
	if random.random() < prob and co:
		return st, False
	if type(node) is tuple:
		arg1, res = recombination_alt(node[1], st, (1/get_size(node[1])) * 0.8, co)
		
		arg2, res = recombination_alt(node[2], st, (1/get_size(node[2])) * 0.8, res)
		
		new_node = (node[0], arg1, arg2)
	else:
		new_node = node
	
	return new_node, res
	
	
# Run an individual (function)
def run(func):
	if type(func) is tuple:
		if len(func) == 4:
			return func[0](func[1], func[2], func[3])
		return func[0](func[1], func[2])
	else:
		return func

if __name__ == "__main__":
	func1 = gen_expr(func_set, term_set, 'grow', 5, 0.3)
	func2 = gen_expr(func_set, term_set, 'grow', 5, 0.6)
	#func3 = recombination(func1, func2)
	print(run(func1))