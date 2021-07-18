# Benjamin Good
# 2021-07-16
# Test program for genetic programming

import math, random

def unpack_args(arg1, arg2):
	a = arg1
	b = arg2
	if type(arg1) is tuple:
		a = arg1[0](arg1[1], arg1[2])
	if type(arg2) is tuple:
		b = arg2[0](arg2[1], arg2[2])
	return a, b

## function definitions go here

def int_value():
	return random.randrange(1000)

def double_value():
	return random.randrange(1000) * random.random()

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
	return a / b
	
## end of function definitions

term_set = [int_value, double_value]
func_set = [mult, div, add, sub]

def gen_expr(func_set, term_set, method, max_depth, set_prob = 1):
	if random.random() < set_prob or max_depth == 0:
		expr = random.choice(term_set)
		expr = expr()
	else:
		func = random.choice(func_set)
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
		# Call the recombination function gain if an argument is a function, otherwise just get terminal from tree
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
	
	

def run(func):
	func[0](arg1, arg2)

if __name__ == "__main__":
	func1 = gen_expr(func_set, term_set, 'grow', 2, len(term_set)/len(func_set))
	func2 = gen_expr(func_set, term_set, 'grow', 2, len(term_set)/len(func_set))
	#func3 = recombination(func1, func2)
	func4 = recombination_alt(func1, pick_node(func2, 1/get_size(func2)), (1/get_size(func1)) * 0.8)
	print(func1)
	print(func2)
	#print(func3)
	print(func4)
	#print(get_size(func))