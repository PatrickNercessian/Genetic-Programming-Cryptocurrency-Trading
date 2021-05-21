import os
import random
import copy

import crypto_data
import helper
import tree
from individual import Individual


class Population:
    def __init__(self, crypto_symbol: str, interval: str, pop_size=100, init_tree_size=2, mutation_probability=0.05,
                 num_dataframes=3):
        self.crypto_symbol = crypto_symbol
        self.interval = interval
        self.pop_size = pop_size
        self.mutation_probability = mutation_probability

        self.current_dataframes = init_dataframes(num_dataframes, crypto_symbol, interval)
        self.directory_name = helper.create_run_folder()

        self.current_generation = 0

        self.individuals = []
        for i in range(pop_size):
            self.individuals.append(Individual(tree.plant_tree(init_tree_size), crypto_symbol, interval))

    def init_dataframes(self, num_dataframes, crypto_symbol, interval):
        self.current_dataframes = []
        for i in range(num_dataframes):
            self.current_dataframes.append(crypto_data.get_random_df(crypto_symbol, interval))

    def next_gen(self):
        if self.pop_size < 1000:
            cutoff = round(0.32 * self.pop_size)
        else:  # Simplifies the 16% for 2000, 8% for 4000, etc.
            cutoff = 320

        new_individuals = []
        while len(new_individuals) < self.pop_size:
            if random.random() < 0.6:  # 60% chance of choosing from the better group
                index_1, index_2 = random.randint(0, cutoff), random.randint(0, cutoff)
                while index_1 == index_2:
                    index_2 = random.randint(0, cutoff)
            else:  # 20% chance of choosing from the worse group
                index_1, index_2 = random.randint(cutoff+1, self.pop_size-1), random.randint(cutoff+1, self.pop_size-1)
                while index_1 == index_2:
                    index_2 = random.randint(cutoff+1, self.pop_size-1)

            if random.random() < self.mutation_probability:
                for i in range(10):  # Try up to 10 times to mutate, if it fails every time, skip
                    new_indiv = mutate(self.individuals[index_1])
                    if new_indiv is not None:
                        new_indiv.tree.node_count = tree.count_children(new_indiv.tree.root)
                        new_individuals.append(new_indiv)
                        break
            else:
                for i in range(10):  # Try up to 10 times to crossover, if it fails every time, skip
                    new_indiv_1, new_indiv_2 = crossover(self.individuals[index_1], self.individuals[index_2])

                    new_indiv_1.tree.node_count = tree.count_children(new_indiv_1.tree.root)
                    new_indiv_2.tree.node_count = tree.count_children(new_indiv_2.tree.root)

                    if new_indiv_1 is not None and new_indiv_2 is not None:
                        if len(new_individuals) < self.pop_size - 1:  # if there's room for 2
                            new_individuals.extend([new_indiv_1, new_indiv_2])
                        else:
                            new_individuals.append(new_indiv_1)
                        break
                    elif new_indiv_1 is not None:
                        new_individuals.append(new_indiv_1)
                    elif new_indiv_2 is not None:
                        new_individuals.append(new_indiv_2)

        self.current_dataframes = init_dataframes(len(self.current_dataframes), self.crypto_symbol, self.interval)
        self.current_generation += 1
        self.individuals = new_individuals

    def evaluate_and_sort(self):
        for indiv in self.individuals:
            sum_balance = 0
            for df in self.current_dataframes:
                sum_balance += indiv.evaluate(df)
            indiv.fitness = sum_balance / len(self.current_dataframes)

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

    node_1, parent_1, which_child_1 = indiv_1_copy.tree.random_node(indiv_1_copy.tree.root)
    node_2, parent_2, which_child_2 = indiv_2_copy.tree.random_node(indiv_2_copy.tree.root)

    expected_types_1 = indiv_1_copy.tree.get_expected(parent_1, which_child_1)
    expected_types_2 = indiv_2_copy.tree.get_expected(parent_2, which_child_2)

    possible_set_1 = []
    for i in expected_types_1:
        for j in i:
            possible_set_1.append(j)

    possible_set_2 = []
    for i in expected_types_2:
        for j in i:
            possible_set_2.append(j)

    # TODO merge var_type lists of existing tree and new subtree

    if node_2.value in possible_set_1:
        if parent_1 is None:  # Meaning root was randomly chosen
            indiv_1_copy.tree.root = node_2
        elif which_child_1 == 0:
            parent_1.left = node_2
        elif which_child_1 == 1:
            parent_1.middle = node_2
        else:  # which_child_1 == 2
            parent_1.right = node_2

        indiv_1_copy.code = tree.decode_in_order(indiv_1_copy.tree.root)
    else:
        indiv_1_copy = None

    if node_1.value in possible_set_2:
        if parent_2 is None:  # Meaning root was randomly chosen
            indiv_2_copy.tree.root = node_1
        elif which_child_2 == 0:
            parent_2.left = node_1
        elif which_child_2 == 1:
            parent_2.middle = node_1
        else:  # which_child_2 == 2
            parent_2.right = node_1

        indiv_2_copy.code = tree.decode_in_order(indiv_2_copy.tree.root)

    else:
        indiv_2_copy = None

    return indiv_1_copy, indiv_2_copy


def mutate(indiv):
    indiv_copy = copy.deepcopy(indiv)

    node, parent, which_child = indiv_copy.tree.random_node(indiv_copy.tree.root)
    expected_types = indiv_copy.tree.get_expected(parent, which_child)

    random_subtree = tree.plant_tree(2)  # TODO tweak max_depth parameter

    # TODO merge var_type lists of existing tree and new subtree

    possible_set = []
    for i in expected_types:
        for j in i:
            possible_set.append(j)

    if random_subtree.root.value in possible_set:
        if parent is None:
            indiv_copy.tree = random_subtree
        elif which_child == 0:
            parent.left = random_subtree.root
        elif which_child == 1:
            parent.middle = random_subtree.root
        else:  # which_child == 2
            parent.right = random_subtree.root
            
        indiv_copy.code = tree.decode_in_order(indiv_copy.tree.root)

        return indiv_copy
    else:
        return None


# Algorithm for evaluating validity during variation operations
# 1. Continuously pick random available branch, and have an increasing probability of selecting node as subtree
# 2. Keep reference of parent and which branch movement (e.g. left child)
# 3. Once new subtree is placed, call get_expected on parent and which_child and check validity
