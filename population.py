import math
import os
import random
import copy
import time

import crypto_data
import helper
import tree
from tree import Tree
from node import Node
from individual import Individual


class Population:
    def __init__(self, crypto_symbol: str, interval: str, pop_size=1000, init_tree_size=5, num_generations=10,
                 mutation_probability=0.05, final_num_dataframes=3):
        self.crypto_symbol = crypto_symbol
        self.interval = interval
        self.pop_size = pop_size
        self.init_tree_size = init_tree_size
        self.num_generations = num_generations
        self.mutation_probability = mutation_probability
        self.final_num_dataframes = final_num_dataframes

        self.current_dataframes = init_dataframes(1, crypto_symbol, interval)
        self.directory_name = helper.create_run_folder()

        self.current_generation = 0

        self.individuals = []

    def run(self):
        # Initiating population
        for i in range(self.pop_size):
            self.individuals.append(Individual(tree.plant_tree(self.init_tree_size), self.crypto_symbol, self.interval))
        self.evaluate_and_sort()

        # Running evolution
        for i in range(self.num_generations):
            self.next_gen()
            self.evaluate_and_sort()

    def next_gen(self):
        if self.pop_size < 1000:
            cutoff = round(0.32 * self.pop_size)
        else:  # Simplifies the 16% for 2000, 8% for 4000, etc.
            cutoff = 320

        new_individuals = []
        while len(new_individuals) < self.pop_size:
            if random.random() < 0.8:  # 80% chance of choosing from the better group
                index_1, index_2 = random.randint(0, cutoff), random.randint(0, cutoff)
                while index_1 == index_2:
                    index_2 = random.randint(0, cutoff)
            else:  # 20% chance of choosing from the worse group
                index_1, index_2 = random.randint(cutoff + 1, self.pop_size - 1), random.randint(cutoff + 1,
                                                                                                 self.pop_size - 1)
                while index_1 == index_2:
                    index_2 = random.randint(cutoff + 1, self.pop_size - 1)

            if random.random() < self.mutation_probability:
                for i in range(10):  # Try up to 10 times to mutate, if it fails every time, skip
                    new_indiv = mutate(self.individuals[index_1])
                    if new_indiv is not None:
                        new_individuals.append(new_indiv)
                        break
            else:
                for i in range(10):  # Try up to 10 times to crossover, if it fails every time, skip
                    new_indiv_1, new_indiv_2 = crossover(self.individuals[index_1], self.individuals[index_2])

                    if new_indiv_1 is None and new_indiv_2 is None:
                        continue
                    if new_indiv_1 is not None:
                        new_individuals.append(new_indiv_1)
                    if new_indiv_2 is not None and len(new_individuals) < self.pop_size:  # if there is room
                        new_individuals.append(new_indiv_2)
                    break

                    # Gen 1: 1, Gen 5: 2, Gen 8: 3
        self.individuals = new_individuals

        self.current_generation += 1
        num_dataframes = int(math.ceil((self.current_generation / self.num_generations) * self.final_num_dataframes))
        self.current_dataframes = init_dataframes(num_dataframes, self.crypto_symbol, self.interval)

    def evaluate_and_sort(self):
        count = 0
        log_file_contents = '\nGeneration ' + str(self.current_generation) + ':\n\n'
        for indiv in self.individuals:
            count += 1
            evaluate_start_time = time.time()
            indiv.fitness = indiv.evaluate(self.current_dataframes)
            message = 'Evaluating Individual ' + str(count) + ' took ' + \
                      str(time.time() - evaluate_start_time) + ' seconds.\n'
            log_file_contents += message
            print(message)

        with open(self.directory_name + os.sep + self.directory_name + '_log.txt', 'a') as log_file:
            log_file.write(log_file_contents)

        self.individuals.sort(reverse=True, key=lambda x: x.fitness)
        all_code = self.get_all_code()
        print(all_code)

        with open(self.directory_name + os.sep + 'Generation ' + str(self.current_generation) + '.txt', 'w') as file:
            file_contents = ""
            for df in self.current_dataframes:
                file_contents += df.to_string() + '\n\n\n'
            file_contents += all_code
            file.write(file_contents)

    def get_all_code(self):
        all_code = '\n----------------------------------------\n'
        for indiv in self.individuals:
            all_code += 'Fitness: ' + str(indiv.fitness) + '\nCode:\n' + indiv.code + '\n\n'
        all_code += '----------------------------------------\n'
        return all_code


def init_dataframes(num_dataframes, crypto_symbol, interval):
    current_dataframes = []
    for i in range(num_dataframes):
        current_dataframes.append(crypto_data.get_random_df(crypto_symbol, interval))
    return current_dataframes


def crossover(indiv_1: Individual, indiv_2: Individual):
    # TODO issue where part of the expectation is coded in grow_tree() function, either move all to get_expectation
    # TODO or just copy that code here too

    # TODO maybe the above is wrong, don't need the expectations that are in grow_tree()

    indiv_1_copy, indiv_2_copy = copy.deepcopy(indiv_1), copy.deepcopy(indiv_2)

    node_1, parent_1, which_child_1 = indiv_1_copy.tree.select_random_node(indiv_1_copy.tree.root)
    node_2, parent_2, which_child_2 = indiv_2_copy.tree.select_random_node(indiv_2_copy.tree.root)

    expected_types_1, _ = indiv_1_copy.tree.get_expected(parent_1, which_child_1)
    expected_types_2, _ = indiv_2_copy.tree.get_expected(parent_2, which_child_2)

    possible_set_1 = []
    for i in expected_types_1:  # TODO use simplified method of flattening list that's used in tree.py
        for j in i:
            possible_set_1.append(j)

    possible_set_2 = []
    for i in expected_types_2:  # TODO use simplified method of flattening list that's used in tree.py
        for j in i:
            possible_set_2.append(j)

    # TODO merge var_list lists of existing tree and new subtree

    if node_2.value in possible_set_1:
        indiv_1_copy_success = True
        if parent_1 is None:  # Meaning root was randomly chosen
            indiv_1_copy.tree.root = node_2
        elif which_child_1 == 0:
            parent_1.left = node_2
        elif which_child_1 == 1:
            parent_1.middle = node_2
        else:  # which_child_1 == 2
            parent_1.right = node_2

        indiv_1_copy.code = tree.decode_in_order(indiv_1_copy.tree.root)
        indiv_1_copy.tree.node_count = tree.count_children(indiv_1_copy.tree.root)
        merge_var_lists(node_2, indiv_1_copy.tree, indiv_2_copy.tree)
    else:
        indiv_1_copy_success = False

    if node_1.value in possible_set_2:
        indiv_2_copy_success = True
        if parent_2 is None:  # Meaning root was randomly chosen
            indiv_2_copy.tree.root = node_1
        elif which_child_2 == 0:
            parent_2.left = node_1
        elif which_child_2 == 1:
            parent_2.middle = node_1
        else:  # which_child_2 == 2
            parent_2.right = node_1

        indiv_2_copy.code = tree.decode_in_order(indiv_2_copy.tree.root)
        indiv_2_copy.tree.node_count = tree.count_children(indiv_2_copy.tree.root)
        merge_var_lists(node_1, indiv_2_copy.tree, indiv_1_copy.tree)
    else:
        indiv_2_copy_success = False

    return indiv_1_copy if indiv_1_copy_success else None, indiv_2_copy if indiv_2_copy_success else None


def mutate(indiv: Individual):
    indiv_copy = copy.deepcopy(indiv)

    node, parent, which_child = indiv_copy.tree.select_random_node(indiv_copy.tree.root)
    expected_types, _ = indiv_copy.tree.get_expected(parent, which_child)

    # TODO tweak max_depth parameter
    # TODO pass in indiv's var_list and allow plant_tree to use those vars while growing
    #                                                               (maybe just grow the original tree from random node)
    random_subtree = tree.plant_tree(2)

    possible_set = []
    for i in expected_types:  # TODO use simplified method of flattening list that's used in tree.py
        for j in i:
            possible_set.append(j)

    if random_subtree.root.value in possible_set:
        node = random_subtree.root

        if parent is None:
            indiv_copy.tree = random_subtree
        elif which_child == 0:
            parent.left = node
        elif which_child == 1:
            parent.middle = node
        else:  # which_child == 2
            parent.right = node

        indiv_copy.code = tree.decode_in_order(indiv_copy.tree.root)
        indiv_copy.tree.node_count = tree.count_children(indiv_copy.tree.root)
        merge_var_lists(node, indiv_copy.tree, random_subtree)

        return indiv_copy
    else:
        return None


def merge_var_lists(implant_node: Node, vary_tree: Tree, original_tree: Tree):
    for used_var_name in set(tree.get_used_variables(implant_node)):
        if used_var_name not in vary_tree.var_name_list:  # if vary_tree doesn't have this var
            v = next(y for y in original_tree.var_list if y.name == used_var_name)
            vary_tree.append_var(v)

# Algorithm for evaluating validity during variation operations
# 1. Continuously pick random available branch, and have an increasing probability of selecting node as subtree
# 2. Keep reference of parent and which branch movement (e.g. left child)
# 3. Once new subtree is placed, call get_expected on parent and which_child and check validity
