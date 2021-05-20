from node import Node
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
        self.highest_depth = 1

        # terminal set (can be added to)  # TODO add df_indicators once relevant function nodes are added
        self.var_type = ['should_buy', 'stop_loss', 'confidence', 'recent_rsi']

    def new_var(self):
        last_var: str = self.var_type[-1]
        if last_var.startswith('v'):
            new_var = 'v' + str(int(last_var[1:]) + 1)
        else:
            new_var = 'v0'
        self.var_type.append(new_var)
        return new_var

    def random_node(self, node: Node, parent: Node = None, which_child: int = None):
        p = random.random()

        if node is None:  # Restart if you never selected a node
            return self.random_node(self.root)

        # TODO maybe make this probability increase as you traverse tree e.g add 1 to numerator
        if p < (1 / self.highest_depth):
            return node, parent, which_child

        # TODO less readable but maybe faster
        # if node.left:
        #     if node.right:
        #         if random.random() < 0.5:
        #             return self.random_node(node.left, node, 0)
        #         else:
        #             return self.random_node(node.right, node, 2)
        #     else:
        #         return self.random_node(node.left, node, 0)
        # elif node.right:
        #     return self.random_node(node.right, node, 2)
        # elif node.middle:
        #     return self.random_node(node.middle, node, 1)

        if node.left and node.right:
            if random.random() < 0.5:
                return self.random_node(node.left, node, 0)
            else:
                return self.random_node(node.right, node, 2)
        elif node.middle:
            return self.random_node(node.middle, node, 1)
        elif node.left and not node.right:
            return self.random_node(node.left, node, 0)
        elif not node.left and node.right:
            return self.random_node(node.right, node, 2)
        else:  # if terminal node with no children
            return self.random_node(self.root)

    #  which_child: 0 for left child, 1 for middle child, 2 for right child
    def get_expected(self, parent: Node, which_child: int, grow_freely=True):
        expected_types = [function_set, self.var_type]

        if parent is None:  # if root
            return expected_types

        if parent.value in function_set:
            if parent.value in unary_operator_type:
                if which_child in [0, 2]:
                    expected_types = []
                elif which_child == 1:
                    expected_types = [unary_operator_type, binary_operator_type, self.var_type] if grow_freely \
                        else [self.var_type]  # we should stunt further growth
            elif parent.value in binary_operator_type:
                if which_child in [0, 2]:
                    expected_types = [unary_operator_type, binary_operator_type, self.var_type] if grow_freely \
                        else [self.var_type]  # we should stunt further growth
                elif which_child == 1:
                    expected_types = []
            elif parent.value == '\n':  # TODO maybe use 'nothing' node as possible expected_type
                if which_child in [0, 2]:
                    expected_types = [assignment_type, line_type, if_type, while_type, for_type] if grow_freely \
                        else [assignment_type]  # we should stunt further growth
                elif which_child == 1:
                    expected_types = []

            elif parent.value == 'for ___:':
                if which_child == 0:
                    expected_types = []
                elif which_child == 1:
                    expected_types = [in_type]
                elif which_child == 2:
                    expected_types = [block_type]
            elif parent.value == 'in':
                if which_child in [0, 2]:
                    expected_types = [self.var_type]
                elif which_child == 1:
                    expected_types = []

            elif parent.value == 'while ___:':
                if which_child == 0:
                    expected_types = []
                elif which_child == 1:
                    expected_types = [boolean_type, self.var_type] if grow_freely else [self.var_type]
                elif which_child == 2:
                    expected_types = [block_type]
            elif parent.value in ['if ___:', 'elif ___:']:
                if which_child == 0:
                    expected_types = []
                elif which_child == 1:
                    expected_types = [boolean_type, self.var_type] if grow_freely else [self.var_type]
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
                    expected_types = [assignment_type, line_type, if_type, while_type, for_type] if grow_freely \
                        else [assignment_type]
                elif which_child == 2:
                    expected_types = [nothing_type, else_type]
            elif parent.value == 'block':  # to be replaced by '\n ___\n'
                if which_child in [0, 2]:
                    expected_types = []
                elif which_child == 1:
                    expected_types = [assignment_type, line_type, if_type, while_type, for_type] if grow_freely \
                        else [assignment_type]

            elif parent.value == 'and' or parent.value == 'or':
                if which_child in [0, 2]:
                    expected_types = [boolean_type, self.var_type] if grow_freely else [self.var_type]
                elif which_child == 1:
                    expected_types = []
            elif parent.value in boolean_type:  # After if ('and' or 'or'), so that only triggers on other boolean_types
                if which_child in [0, 2]:
                    if grow_freely:
                        expected_types = [unary_operator_type, binary_operator_type, boolean_type, self.var_type]
                    else:
                        expected_types = [self.var_type]
                elif which_child == 1:
                    expected_types = []
            elif parent.value == '=':
                if which_child == 0:
                    expected_types = [self.var_type]
                elif which_child == 1:
                    expected_types = []
                elif which_child == 2:  # TODO issue where it's always choosing self.var_type? maybe bc of max_depth
                    if grow_freely:  # Free to grow
                        expected_types = [unary_operator_type, binary_operator_type, assignment_type, boolean_type,
                                          self.var_type]
                    else:  # we should stunt further growth
                        expected_types = [self.var_type]
            elif parent.value == 'nothing':
                expected_types = []

        else:  # terminal node or 'nothing' node
            expected_types = []

        return expected_types


def count_children(node: Node):
    if node:
        count = 1
        count += count_children(node.left)
        count += count_children(node.right)
        return count
    else:
        return 0


def decode_in_order(root: Node, num_indentations=0):
    if root:
        to_add = root.value
        if to_add != 'nothing':
            code = decode_in_order(root.left, num_indentations)

            if to_add == '\n':
                to_add += (' ' * num_indentations)
            elif (to_add in binary_operator_type) or (to_add in assignment_type) \
                    or (to_add in in_type) or (to_add in boolean_type):
                to_add = ' ' + to_add + ' '
            elif to_add in ['block', 'if-elif-block']:
                to_add = '\n ___\n'

            if root.middle is None:
                code += to_add
            else:
                index_of_blank = to_add.index('___')
                code += to_add[:index_of_blank]

                if to_add == '\n ___\n':
                    code += decode_in_order(root.middle, num_indentations+1)
                else:
                    code += decode_in_order(root.middle, num_indentations)

                code += to_add[index_of_blank+3:]

            code += decode_in_order(root.right, num_indentations)

            return code
    return ''


def plant_tree(max_depth: int):
    root = Node(random.choice(line_type), depth=0)  # TODO right now, line_type is only '\n'
    # root = Node('\n')
    tree = Tree(root)

    root.left = grow_tree(tree, root, 0, 0, max_depth)
    root.middle = grow_tree(tree, root, 1, 0, max_depth)
    root.right = grow_tree(tree, root, 2, 0, max_depth)

    return tree


def grow_tree(tree: Tree, parent: Node, which_child, depth: int, max_depth: int):
    p = random.random()

    if parent.value == '=' and which_child == 0:
        if p < (1 / (len(tree.var_type) + 1)):  # Chance to create new variable if assigning variable
            return Node(tree.new_var(), depth)
        else:
            return Node(random.choice(tree.var_type), depth)
    elif parent.value == 'in':
        if which_child == 0:  # create new variable left of 'in'
            return Node(tree.new_var(), depth)
        elif which_child == 2:  # use existing variable right of 'in'
            return Node(random.choice(tree.var_type), depth)

    expected_types = tree.get_expected(parent, which_child, grow_freely=True if depth < max_depth else False)

    # allow depth to exceed max if function children are required
    if depth < max_depth or tree.var_type not in expected_types:

        possible_set = []
        for i in expected_types:
            for j in i:
                possible_set.append(j)

        if len(possible_set) > 0:
            node = Node(random.choice(possible_set), depth)

            # 50% chance of random constant if a variable is acceptable and parent isn't 'if' or 'while'
            if p < 0.5 and tree.var_type in expected_types and parent.value not in ['if ___:', 'while ___:']:
                node = Node(rand_const(), depth)

            if depth + 1 > tree.highest_depth:
                tree.highest_depth = depth + 1

            node.left = grow_tree(tree, node, 0, depth + 1, max_depth)
            node.middle = grow_tree(tree, node, 1, depth + 1, max_depth)
            node.right = grow_tree(tree, node, 2, depth + 1, max_depth)
            return node
        else:  # parent was terminal node
            return None
    else:  # reached max depth, and terminal node is allowed here
        # 50% chance of picking random variable (100% chance if parent is 'if ___:' or 'elif ___:' or 'while ___:')
        if random.random() < 0.5 or parent.value in ['if ___:', 'elif ___:', 'while ___:']:
            return Node(random.choice(tree.var_type), depth)
        else:  # 50% chance of picking random constant
            return Node(rand_const(), depth)


def rand_const():
    p = random.random()
    if p < 0.33:
        const = str(random.choice([True, False]))
    elif p < 0.67:
        const = str(random.uniform(-1024, 1024))  # TODO arbitrary limits, may need tweaking
    else:
        const = str(random.randint(-1024, 1024))
    return const


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
                    tree_str += ' ' * (count_children(node.left.left)+1) * 10
                    print(count_children(node.left.left))

                if node.left.right:
                    tree_str += '-' * (count_children(node.left.right)+1) * 10

            if node.value.startswith('\n'):
                tree_str += '\\n'
                if node.value.endswith('end-block'):
                    tree_str += 'end-block'
            else:
                tree_str += node.value

            if node.right:
                q.put(node.right)

                if node.right.left:
                    tree_str += '-' * (count_children(node.right.left)+1) * 10
                if node.right.right:
                    tree_str += ' ' * (count_children(node.right.right)+1) * 10

            old_depth = node.depth

        return tree_str
    else:
        return ''
