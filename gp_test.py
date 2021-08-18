# Benjamin Good
# 2021-07-16
# Test program for genetic programming

import math, random, sys

sys.setrecursionlimit(2000)

prob = 0.5
reward = 10
cost = 10

def unpack_args(arg1, arg2):
	a = arg1
	b = arg2
	if type(arg1) is list:
		a = run(arg1)
	if type(arg2) is list:
		b = run(arg2)
	return a, b

## function definitions go here

def int_value():
	return random.randrange(1000)

def double_value():
	return random.randrange(1000) * random.random()

def get_prob():
	return prob

def get_reward():
	return reward

def get_cost():
	return cost

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
		return 1
	return a / b

def ifelse(arg1, arg2, arg3):
	if run(arg1):
		return run(arg2)
	else:
		return run(arg3)

def prob_under(arg1):
	return prob < run(arg1)

def reward_over(arg1):
	return reward > run(arg1)

def cost_under(arg1):
	return cost < run(arg1)
	
## end of function definitions

term_set = [get_prob, get_reward, get_cost]
func_set = [prob_under, cost_under, reward_over, ifelse]

def gen_expr(func_set, term_set, method, max_depth, set_prob = 1):
	if random.random() < set_prob or max_depth == 0:
		expr = random.choice(term_set)
	else:
		func = random.choice(func_set)
		if func.__name__ == "ifelse":
			arg1 = gen_expr(func_set, term_set, method, max_depth-1, set_prob)
			arg2 = gen_expr(func_set, term_set, method, max_depth-1, set_prob)
			arg3 = gen_expr(func_set, term_set, method, max_depth-1, set_prob)
			expr = [func, arg1, arg2, arg3]
		else:
			arg1 = gen_expr(func_set, term_set, method, max_depth-1, set_prob)
			expr = [func, arg1]
	return expr

def is_func(prim):
	if globals[str(prim)]:
		return True
	return False

def get_size(node, size=0):
	if type(node) is list:
		size = get_size(node[1], size)
		if len(node) == 4:
			size = get_size(node[2], size)
			size = get_size(node[3], size)
	
	return size + 1

# Pick a node in a tree
# Could be used for recombination/mutation
def pick_node(node, prob):
	if random.random() < prob:
		return node
		
	if type(node) is list:
		args = []
		hits = 0
		for n in node[1:]:
			arg = pick_node(n, 0.3)
			if arg is not None:
				hits += 1
			args.append(arg)
		if hits == 0:
			return None
		else:
			return random.choice([a for a in args if a is not None])

def pick_node_dual(node, term_prob, func_prob):
	r = random.random()
	if node in term_set and r < term_prob:
		return node
	elif node in func_set and r < func_prob:
		return node
		
	if type(node) is list:
		args = []
		hits = 0
		for n in node[1:]:
			p = 1/get_size(n)
			arg = pick_node_dual(n, p, p*4)
			if arg is not None:
				hits += 1
			args.append(arg)
		if hits == 0:
			return None
		else:
			return random.choice([a for a in args if a is not None])
		
#	if type(node) is list:
#		node_arg1 = pick_node(node[1], 1/get_size(node[1]))
#		node_arg2 = pick_node(node[2], 1/get_size(node[2]))
#		if node_arg1 is not None and node_arg2 is not None:
#			return random.choice([node_arg1, node_arg2])
#		if node_arg1 is None:
#			if node_arg2 is None:
#				return None
#			else:
#				return node_arg2
#		else:
#			return node_arg1

def recombination(node, other):
	new_node = None
	arg1 = None
	arg2 = None
	# Get subtree from other parent
	subtree = pick_node(other, 0.3)
	while subtree is None:
		subtree = pick_node(other, 0.3)
	# Potentially use the subtree for copying genetic material to child, otherwise use first parent
	if random.random() < 1/get_size(node) * 0.5:
		node = subtree
	if type(node) is list:
		# Call the recombination function again if an argument is a function, otherwise just get terminal from tree
		new_node = [node[0]]
		for n in node[1:]:
			arg = None
			if type(n) is list:
				arg = recombination(n, other)
			else:
				arg = n
			new_node.append(arg)
#		if type(node[1]) is tuple:
#			arg1 = recombination(node[1], other)
#		else:
#			arg1 = node[1]
			
#		if type(node[2]) is tuple:
#			arg2 = recombination(node[2], other)
#		else:
#			arg2 = node[2]
#		new_node = (node[0], arg1, arg2)
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
	
def eval(ind):
	val = 0
	ind = run(ind)
	if get_size(ind) > 5:
		val -= 10
	if get_size(ind) > 10:
		val -= 20
	if get_size(ind) > 15 :
		val -= 30
	if get_size(ind) > 20:
		val -= 40
	
	if ind == 1:
		val += 50
	elif ind == 0:
		val += 50
	
	return val
	

def run(func):
	if type(func) is not list:
		return func()
	if len(func) == 2:
		return func[0](func[1])
	elif len(func) == 4:
		return func[0](func[1], func[2], func[3])

def main(gens, popsize):
	pool = [gen_expr(func_set, term_set, 'grow', 5, 0.6) for i in range(popsize)]
	
	for gen in range(gens):
		if gen % 5 == 0:
			print("Printing individuals:")
			for ind in pool:
				print(ind)
			print("End of pool")
			
		nextgen = []
		fitness = [eval(ind) for ind in pool]
		for i in range(popsize):
			parents = random.choices(pool, k=2)
			
			child = recombination(parents[0], parents[1])
			
			nextgen.append(child)
			
		pool = nextgen
		#print(run(pool[0]))

if __name__ == "__main__":
	main(100, 12)