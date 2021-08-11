from node import Node
from variable import Variable
from function_set import *

from queue import Queue
import random


# TODO stop this line from being possible (specifically the 196 part): 'if 196 and recent_rsi:'
# Possible syntactic failures:
# 1. specific variable type is required (i.e. boolean for if statement), but other type is present
# 2. new variable is created in a conditional block and referenced elsewhere
# 3. new variable is created and used elsewhere, then the assignment is subsequently removed by variation
# 4. infinite loop on variable that never changes
# 5. for loop iterates over non-iterable variable  TODO need a list of iterable variables apart from current list
# 6. new variable created as left-child of 'in', but is referenced outside of for loop
#                                               (actually possible for other blocks too)
# 7. Indentation messes up  e.g. if a:
#                                   b = 2
#                                c = 1
#                                   d = 0


class Tree:
    def __init__(self, root):
        self.root = root
        self.node_count = count_children(root)
        self.max_depth = -1
        # self.highest_depth = 1  # TODO This is faulty, does not account for crossover or mutation

        # terminal set (can be added to)  # TODO add df_indicators once relevant function nodes are added
        # self.var_list = ['should_buy', 'stop_loss', 'confidence', 'recent_rsi']
        self.var_list = [Variable('confidence', float, 0.0, 1.0),
                         Variable('recent_rsi', float, 0.0, 100.0)]
        self.var_name_list = ['confidence', 'recent_rsi']
        self.float_var_names = ['confidence', 'recent_rsi']
        self.int_var_names = []
        self.bool_var_names = []
        self.list_var_names = []  # TODO irrelevant for now since for loops were taken out

    def grow_tree(self, parent: Node, max_depth: int, current_depth=0):
        parent.left = self.grow_branch(parent, 0, current_depth + 1, max_depth)
        parent.middle = self.grow_branch(parent, 1, current_depth + 1, max_depth)
        parent.right = self.grow_branch(parent, 2, current_depth + 1, max_depth)

    def grow_branch(self, parent: Node, which_child, depth: int, max_depth: int):
        p = random.random()

        if parent.value == '=' and which_child == 0:  # if assigning variable
            if p < (1 / (len(self.var_name_list) + 1)):  # Chance to create new variable
                new_var = self.new_var()
                self.append_var(new_var)
                return Node(new_var.name, depth)
            else:
                temp_list = [x for x in self.var_name_list if x != 'recent_rsi']  # Tested: faster than loop re-choosing
                return Node(random.choice(temp_list), depth)
        # elif parent.value == 'in' and which_child == 0:  # always create new variable left of 'in'
        #     new_var = tree.new_var()
        #     tree.append_var(new_var)
        #     return Node(new_var.name, depth)

        expected_types, expected_variable_types = self.get_expected(parent, which_child, grow_freely=depth < max_depth)
        is_float_allowed = float in expected_variable_types
        is_int_allowed = int in expected_variable_types
        is_bool_allowed = bool in expected_variable_types

        num_allowed = is_float_allowed + is_int_allowed + is_bool_allowed

        is_function_required = not num_allowed or (parent.value in ['if ___:', 'elif ___:', 'while ___:']
                                                   and not self.bool_var_names)
        if depth < max_depth or is_function_required:  # allow depth to exceed max if function children are required
            possible_set = []
            for i in expected_types:
                possible_set.extend(i)

            if possible_set:
                node = Node(random.choice(possible_set), depth)

                num_allowed = is_float_allowed + is_int_allowed + is_bool_allowed
                # 50% chance of random constant if a variable is acceptable and parent isn't 'if', 'elif', or 'while'
                if p < 0.5 and num_allowed and parent.value not in ['if ___:', 'elif ___:', 'while ___:']:
                    rand = random.random() * num_allowed
                    # (1 / num_allowed)% probability of executing if float allowed, 0% probability if not
                    if rand < is_float_allowed:
                        node = Node(str(random.gauss(0, 100)), depth)
                    elif rand < is_float_allowed + is_int_allowed:  # same probability of above
                        node = Node(str(int(random.gauss(0, 100))), depth)
                    else:  # elif rand < is_float_allowed + is_int_allowed + is_bool_allowed
                        node = Node(str(random.choice([True, False])), depth)  # same probability as above

                # if depth + 1 > tree.highest_depth:
                #     tree.highest_depth = depth + 1

                node.left = self.grow_branch(node, 0, depth + 1, max_depth)
                node.middle = self.grow_branch(node, 1, depth + 1, max_depth)
                node.right = self.grow_branch(node, 2, depth + 1, max_depth)
                return node
            else:  # parent was terminal node
                return None
        else:  # reached max depth, and terminal node is allowed here
            rand = random.random() * (is_float_allowed + is_int_allowed + is_bool_allowed)

            # (1 / num allowed types)% chance of executing if float allowed, 0% chance if not
            if rand < is_float_allowed:
                if p < 0.5:  # 50% chance of random float variable
                    return Node(random.choice(self.float_var_names), depth)
                else:  # 50% chance of float constant
                    return Node(str(random.gauss(0, 100)), depth)

            # (1 / num allowed types)% chance of executing if int allowed, 0% chance if not
            elif rand < is_float_allowed + is_int_allowed:
                if p < 0.5 and self.int_var_names:  # 50% chance of random int variable if one exists
                    return Node(random.choice(self.int_var_names), depth)
                else:  # 50% chance of int constant
                    return Node(str(int(random.gauss(0, 100))), depth)

            # (1 / num allowed types)% chance of executing if bool allowed, 0% chance if not
            else:  # elif rand < is_float_allowed + is_int_allowed + is_bool_allowed:
                # 50% chance of random bool variable (100% chance if parent is 'if', 'elif', or 'while')
                if p < 0.5 and self.bool_var_names or parent.value in ['if ___:', 'elif ___:', 'while ___:']:
                    return Node(random.choice(self.bool_var_names), depth)
                else:  # 50% chance of random bool constant (0% chance if parent is 'if', 'elif', or 'while')
                    return Node(str(random.choice([True, False])), depth)

    #  which_child: 0 for left child, 1 for middle child, 2 for right child
    def get_expected(self, parent: Node, which_child: int, grow_freely=True):
        expected_types = [function_set, self.var_name_list]
        expected_variable_types = []

        if parent is None:  # if root
            return expected_types

        if parent.value in function_set:
            if parent.value in unary_operator_type:
                if which_child in [0, 2]:
                    expected_types = []
                elif which_child == 1:
                    expected_variable_types = [float, int]
                    expected_types = [self.int_var_names, self.float_var_names]
                    if grow_freely:
                        expected_types.extend([unary_operator_type, binary_operator_type])
            elif parent.value in binary_operator_type:
                if which_child in [0, 2]:
                    expected_variable_types = [float, int]
                    expected_types = [self.int_var_names, self.float_var_names]
                    if grow_freely:
                        expected_types.extend([unary_operator_type, binary_operator_type])
                elif which_child == 1:
                    expected_types = []
            elif parent.value == '\n':  # TODO maybe use 'nothing' node as possible expected_type
                if which_child in [0, 2]:
                    expected_types = [assignment_type]
                    if grow_freely:
                        expected_types.extend([line_type, if_type, while_type])  # for_type
                elif which_child == 1:
                    expected_types = []

            # elif parent.value == 'for ___:':
            #     if which_child == 0:
            #         expected_types = []
            #     elif which_child == 1:
            #         expected_types = [in_type]
            #     elif which_child == 2:
            #         expected_types = [block_type]
            # elif parent.value == 'in':
            #     if which_child in [0, 2]:
            #         expected_types = [self.list_var_names]
            #     elif which_child == 1:
            #         expected_types = []

            elif parent.value == 'while ___:':
                if which_child == 0:
                    expected_types = []
                elif which_child == 1:
                    expected_variable_types = [bool]
                    expected_types = []
                    if self.bool_var_names:
                        expected_types.append(self.bool_var_names)
                    if grow_freely or not self.bool_var_names:
                        expected_types.append(boolean_type)
                elif which_child == 2:
                    expected_types = [block_type]
            elif parent.value in ['if ___:', 'elif ___:']:
                if which_child == 0:
                    expected_types = []
                elif which_child == 1:
                    expected_variable_types = [bool]
                    expected_types = []
                    if self.bool_var_names:
                        expected_types.append(self.bool_var_names)
                    if grow_freely or not self.bool_var_names:
                        expected_types.append(boolean_type)
                elif which_child == 2:
                    expected_types = [if_elif_block_type]
            elif parent.value == 'else:':
                if which_child in [0, 1]:
                    expected_types = []
                elif which_child == 2:
                    expected_types = [block_type]

            elif parent.value == 'if-elif-block':  # to be replaced by '\n ___\n'
                if which_child == 0:
                    expected_types = []
                elif which_child == 1:
                    expected_types = [assignment_type]
                    if grow_freely:
                        expected_types.extend([line_type, if_type, while_type])  # for_type
                elif which_child == 2:
                    expected_types = [nothing_type, else_type]
            elif parent.value == 'block':  # to be replaced by '\n ___\n'
                if which_child in [0, 2]:
                    expected_types = []
                elif which_child == 1:
                    expected_types = [assignment_type]
                    if grow_freely:
                        expected_types.extend([line_type, if_type, while_type])  # for_type

            elif parent.value in ['and', 'or']:
                if which_child in [0, 2]:
                    expected_variable_types = [bool]
                    expected_types = []
                    if self.bool_var_names:
                        expected_types.append(self.bool_var_names)
                    if grow_freely or not self.bool_var_names:
                        expected_types.append(boolean_type)
                elif which_child == 1:
                    expected_types = []
            elif parent.value in ['>=', '<=', '>', '<']:
                if which_child in [0, 2]:
                    expected_variable_types = [float, int]
                    expected_types = [self.int_var_names, self.float_var_names]
                    if grow_freely:
                        expected_types.extend([unary_operator_type, binary_operator_type])
                elif which_child == 1:
                    expected_types = []
            elif parent.value in ['==', '!=']:
                if which_child in [0, 2]:
                    expected_variable_types = [float, int, bool]
                    expected_types = [self.int_var_names, self.float_var_names, self.bool_var_names]
                    if grow_freely:
                        expected_types.extend([unary_operator_type, binary_operator_type, boolean_type])
                elif which_child == 1:
                    expected_types = []

            elif parent.value == '=':
                if which_child == 0:  # TODO This only executes during crossover or mutation
                    expected_variable_types = [float, int, bool]
                    expected_types = [[x for x in self.var_name_list if x != 'recent_rsi']]
                elif which_child == 1:
                    expected_types = []
                elif which_child == 2:
                    left_var_type = next(x for x in self.var_list if x.name == parent.left.value).v_type

                    if left_var_type == int or left_var_type == float:
                        expected_variable_types = [int, float]
                        expected_types = [self.int_var_names, self.float_var_names]
                        if grow_freely:
                            expected_types.extend([unary_operator_type, binary_operator_type])
                    elif left_var_type == bool:
                        expected_types = []
                        if self.bool_var_names:
                            expected_types.append(self.bool_var_names)
                        if grow_freely or not self.bool_var_names:
                            expected_types.append(boolean_type)
                    elif left_var_type == list:  # TODO useless for now, and written incorrectly: chance of no list vars
                        expected_types = [self.list_var_names]

            elif parent.value == 'nothing':
                expected_types = []

        else:  # terminal node or 'nothing' node
            expected_types = []

        return expected_types, expected_variable_types

    def new_var(self):  # TODO tentative issue of creating new var with same name as temporary var from for loop
        last_var_name: str = self.var_name_list[-1]
        if last_var_name.startswith('v'):
            new_var_name = 'v' + str(int(last_var_name[1:]) + 1)
        else:
            new_var_name = 'v0'

        p = random.random()
        if p < 0.34:
            v = Variable(new_var_name, float, -200.0, 200.0)  # TODO arbitrary limits, may tweak
        elif p < 0.67:
            v = Variable(new_var_name, int, -200, 200)  # TODO arbitrary limits, may tweak
        else:
            v = Variable(new_var_name, bool, False, True)

        return v

    def append_var(self, var: Variable):
        self.var_list.append(var)
        self.var_name_list.append(var.name)
        if var.v_type == float:
            self.float_var_names.append(var.name)
        elif var.v_type == int:
            self.int_var_names.append(var.name)
        elif var.v_type == bool:
            self.bool_var_names.append(var.name)

    def select_random_node(self, node: Node, parent: Node = None, which_child: int = None):
        p = random.random()
        # if node is None:  # Restart if you never selected a node
        #     return self.random_node(self.root)
        if p < (node.depth / self.node_count):
            return node, parent, which_child

        possible_paths = []
        if node.left:
            possible_paths.append(0)
        if node.middle:
            possible_paths.append(1)
        if node.right:
            possible_paths.append(2)

        if not possible_paths:  # if terminal node with no children
            return self.select_random_node(self.root)

        rand_path = random.choice(possible_paths)

        if rand_path == 0:
            return self.select_random_node(node.left, node, 0)
        elif rand_path == 1:
            return self.select_random_node(node.middle, node, 1)
        elif rand_path == 2:
            return self.select_random_node(node.right, node, 2)


def count_children(node: Node):
    if node:
        count = 1
        count += count_children(node.left)
        count += count_children(node.middle)
        count += count_children(node.right)
        return count
    else:
        return 0


def get_used_variables(node: Node):
    if node:
        used_var_list = []
        used_var_list.extend(get_used_variables(node.left))
        used_var_list.extend(get_used_variables(node.middle))
        used_var_list.extend(get_used_variables(node.right))
        if node.value.startswith('v'):
            used_var_list.append(node.value)
        return used_var_list
    else:
        return []


def decode_in_order(node: Node, num_indentations=0):
    if node:
        to_add = node.value
        if to_add != 'nothing':
            code = decode_in_order(node.left, num_indentations)

            if to_add == '\n':
                to_add += (' ' * num_indentations)
            elif (to_add in binary_operator_type) or (to_add in assignment_type) \
                    or (to_add in boolean_type):  # or (to_add in in_type)
                to_add = ' ' + to_add + ' '
            elif to_add in ['block', 'if-elif-block']:
                to_add = '\n' + (' ' * (num_indentations + 1)) + '___\n'

            if node.middle is None:
                code += to_add
            else:
                index_of_blank = to_add.index('___')
                code += to_add[:index_of_blank]

                if to_add.startswith('\n') and to_add.endswith('___\n'):
                    code += decode_in_order(node.middle, num_indentations + 1)
                else:
                    code += decode_in_order(node.middle, num_indentations)

                code += to_add[index_of_blank + 3:]

            code += decode_in_order(node.right, num_indentations)
            return code
    return ''


def plant_tree(max_depth: int):
    # root = Node(random.choice(line_type), depth=0)
    tree = Tree(Node('\n', depth=0))  # right now, line_type is only '\n'
    tree.max_depth = max_depth

    tree.grow_tree(tree.root, max_depth)
    tree.node_count = count_children(tree.root)

    return tree


def to_string(root: Node):
    if root:
        q = Queue()
        q.put(root)
        tree_str = ''

        old_depth = 0
        while not q.empty():
            node = q.get()

            if node.depth > old_depth:
                print("node.value", node.value)
                print('node.depth:', node.depth)
                print('old_depth:', old_depth)

                tree_str += '\n'

            if node is None:
                continue

            if node.left:
                q.put(node.left)

                print(node.left.left)

                if node.left.left:
                    tree_str += ' ' * (count_children(node.left.left) + 1) * 10
                    print(count_children(node.left.left))

                if node.left.right:
                    tree_str += '-' * (count_children(node.left.right) + 1) * 10

            if node.value.startswith('\n'):
                tree_str += '\\n'
                if node.value.endswith('end-block'):
                    tree_str += 'end-block'
            else:
                tree_str += node.value

            if node.right:
                q.put(node.right)

                if node.right.left:
                    tree_str += '-' * (count_children(node.right.left) + 1) * 10
                if node.right.right:
                    tree_str += ' ' * (count_children(node.right.right) + 1) * 10

            old_depth = node.depth

        return tree_str
    else:
        return ''
