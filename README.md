This program is intended to implement Genetic Programming, an evolutionary algorithm using a tree-based representation of python code. The evolution is generational. Crossover (a very high probability of occurring) is defined as swapping two random subtrees of the parents to create two new offspring. Mutation (a very low probability of occurring) is defined as replacing a random subtree with a random newly generated subtree of a parent to create a new offspring. Parent selection involves 80% of new offspring coming from the top x% of the population, where x depends on the population size (for 1000, x is 32). Finally, fitness is determined by pseudo-trading based on the individual's code.