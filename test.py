import math

import crypto_data
from crypto_data import *
from individual import Individual
from population import Population, mutate, crossover
from tree import *


def test_tree():
    # x = 5
    a = Node('x', 3)
    b = Node('=', 2)
    b.left = a
    c = Node('5', 3)
    b.right = c
    d = Node('\n', 1)
    d.left = b

    # if x == 5:
    e = Node('if', 3)
    f = Node('x', 5)
    g = Node('==', 4)
    g.left = f
    e.right = g
    h = Node('5', 5)
    g.right = h
    i = Node(':', 2)
    i.left = e
    d.right = i

    #   y = 10
    j = Node('x', 5)
    k = Node('=', 4)
    k.left = j
    l = Node('10', 5)
    k.right = l
    m = Node('\n', 3)
    m.left = k
    i.right = m

    #   z = 'Testing'
    n = Node('z', 6)
    o = Node('=', 5)
    p = Node('\'Testing\'', 6)
    # q = Node('\n')
    q = Node('\nend-block', 4)
    q.left = o
    o.left = n
    o.right = p
    m.right = q

    r = Node('print(\'Output:\', x)', 0)
    r.left = d

    root = r
    # print(count_children(i))
    # print(to_string(i))
    code = decode_in_order(root)
    print('\n\n' + code + '\n\n')
    exec(code)


def decision_example1(recent_rsi):
    if recent_rsi < 30:
        should_buy = True
        confidence = (30 - recent_rsi) / 30
    elif recent_rsi > 70:
        should_buy = False
        confidence = (recent_rsi - 70) / 30


def test_example_algorithm():
    if_node = Node('if ___:', 1)

    less = Node('<', 2)
    less.left = Node('recent_rsi', 3)
    less.right = Node('30', 3)

    if_node.middle = less

    block = Node('if-elif-block', 2)
    if_node.right = block

    line1 = Node('\n', 3)
    block.middle = line1

    equals1 = Node('=', 4)
    equals1.left = Node('should_buy', 5)
    equals1.right = Node('True', 5)
    line1.left = equals1

    line2 = Node('\n', 4)
    line1.right = line2

    equals2 = Node('=', 5)
    line2.left = equals2
    equals2.left = Node('v0', 6)
    minus = Node('-', 6)
    equals2.right = minus
    minus.left = Node('30', 7)
    minus.right = Node('recent_rsi', 7)

    equals3 = Node('=', 5)
    line2.right = equals3
    equals3.left = Node('confidence', 6)
    divide = Node('/', 6)
    equals3.right = divide
    divide.left = Node('v0', 7)
    divide.right = Node('20', 7)

    elif_node = Node('elif ___:', 3)
    block.right = elif_node

    zgreater = Node('>', 4)
    zgreater.left = Node('recent_rsi', 5)
    zgreater.right = Node('60', 5)

    elif_node.middle = zgreater

    zblock = Node('if-elif-block', 4)
    elif_node.right = zblock

    zline1 = Node('\n', 5)
    zblock.middle = zline1
    zblock.right = Node('nothing', 5)

    zequals1 = Node('=', 6)
    zequals1.left = Node('should_buy', 7)
    zequals1.right = Node('False', 7)
    zline1.left = zequals1

    zline2 = Node('\n', 6)
    zline1.right = zline2

    zequals2 = Node('=', 7)
    zline2.left = zequals2
    zequals2.left = Node('v0', 8)
    zminus = Node('-', 8)
    zequals2.right = zminus
    zminus.left = Node('recent_rsi', 9)
    zminus.right = Node('60', 9)

    zequals3 = Node('=', 8)
    zline2.right = zequals3
    zequals3.left = Node('confidence', 9)
    zdivide = Node('/', 9)
    zequals3.right = zdivide
    zdivide.left = Node('v0', 10)
    zdivide.right = Node('20', 10)

    root = if_node
    code = decode_in_order(root)
    print('\n\n' + code + '\n\n')

    tree = Tree(root)

    print(count_children(root))

    crypto_symbol = 'BTCUSDT'
    interval = '1d'
    individual = Individual(tree, crypto_symbol, interval)

    sum = 0
    num_runs = 30
    for i in range(num_runs):
        balance = individual.evaluate(crypto_data.get_random_df(crypto_symbol, interval))
        print('Balance:', balance)
        sum += balance
    print('Fitness:', sum / num_runs)


def test1():
    tree = plant_tree(2)
    crypto_symbol = 'BTCUSDT'
    interval = '3m'
    individual = Individual(tree, crypto_symbol, interval)
    individual.evaluate(crypto_data.get_random_df(crypto_symbol, interval))


def test_plant_tree():
    # for i in range(30):
    tree = plant_tree(4)
    print(count_children(tree.root))
    print(decode_in_order(tree.root), '\n\n')
    print(get_used_variables(tree.root))
    print()


def test_crypto_data():
    get_all_crypto_data_online('BTCUSDT', '')


def test2():
    the_code = "x = 3\na = 1\nb = 2\nreturn_me = a + b"

    x = 5
    loc = {"x": x}
    exec(the_code, loc)
    # return_workaround = loc['x']
    print(loc['x'])  # 3


def test3():
    x = {'y': 3, 'z': 'yes'}
    x.update({'y': 5})
    print(x['y'])


def test_create_folder():
    helper.create_run_folder()


def test_confidence_bool():
    # WORKS:
    a = Node('=', 0)
    a.left = Node('confidence', 1)
    b = Node('<=', 1)
    a.right = b
    b.left = Node('recent_rsi', 2)
    b.right = Node('5', 2)

    tree = Tree(a)
    indiv = Individual(tree, 'BTCUSDT', '1d')
    indiv.evaluate([crypto_data.get_random_df('BTCUSDT', '1d'), crypto_data.get_random_df('BTCUSDT', '1d')])

    # But this one doesn't work
    # a = Node('=', 0)
    # a.left = Node('confidence', 1)
    # b = Node('<=', 1)
    # a.right = b
    # b.left = Node('recent_rsi', 2)
    #
    # c = Node('==', 2)
    # b.right = c
    # c.left = Node('-258', 3)
    # c.right = Node('confidence', 3)
    #
    # tree = Tree(a)
    # indiv = Individual(tree, 'BTCUSDT', '1d')
    # indiv.evaluate([crypto_data.get_random_df('BTCUSDT', '1d')])


def test_mutation():
    for _ in range(30):
        tree = plant_tree(3)
        indiv = Individual(tree, 'BTCUSDT', '3m')
        mutated_indiv = mutate(indiv)
        print('OG Indiv:\n' + indiv.code)
        print('\n\nMutated Indiv:\n' + mutated_indiv.code)
        print('\n\n\n')


def test_crossover():
    tree_1, tree_2 = plant_tree(4), plant_tree(4)
    indiv_1, indiv_2 = Individual(tree_1, 'BTCUSDT', '3m'), Individual(tree_2, 'BTCUSDT', '3m')
    offspring_1, offspring_2 = crossover(indiv_1, indiv_2)

    print('parent 1:\n' + indiv_1.code + '\n\n' + 'parent 2:\n' + indiv_2.code + '\n\n\n')

    if offspring_1 is not None:
        print(offspring_1.code + '\n\n')
    else:
        print('Crossover for offspring_1 failed... Likely an invalid subtree was placed')

    if offspring_2 is not None:
        print(offspring_2.code)
    else:
        print('Crossover for offspring_2 failed... Likely an invalid subtree was placed')


def test_mutated_crossover():
    tree = plant_tree(4)
    indiv = Individual(tree, 'BTCUSDT', '3m')
    print('OG tree:\n' + indiv.code)

    offspring_1, offspring_2 = crossover(indiv, indiv)

    if offspring_1 is not None:
        print('\n\n1:\n' + offspring_1.code + '\n\n')
    else:
        print('Crossover for offspring_1 failed... Likely an invalid subtree was placed')

    if offspring_2 is not None:
        print('\n\n2:\n' + offspring_2.code + '\n\n')
    else:
        print('Crossover for offspring_2 failed... Likely an invalid subtree was placed')


def test_population():
    population = Population('BTCUSDT', '1d', pop_size=50)
    population.run()


if __name__ == '__main__':
    # test_crossover()
    # test_example_algorithm()
    # test_plant_tree()
    test_mutated_crossover()
    # test_population()
    # test_mutation()
    # test_confidence_bool()
    # x = 3 > 5 <= 12
    # y = 30 <= -258 == 1.0
    # print(type(x))
    # print(type(y))

    # x = True
    # import random
    # p = random.random()
    # if p * 3 < True:
    #     print('yes', p)
    # else:
    #     print('no', p)

    # var_name_list = ['recent_rsi', 'confidence', 'v0', 'v1']
    # import time
    # start = time.time()
    # rand = random.choice(var_name_list)
    # while rand == 'recent_rsi':
    #     print('yuhhhhhhhhhhhhh')
    #     rand = random.choice(var_name_list)
    # first_time = time.time() - start
    # print('First took', first_time, 'seconds')
    #
    # start = time.time()
    # new_list = [x for x in var_name_list if x != 'recent_rsi']
    # rand = random.choice(new_list)
    # second_time = time.time() - start
    # print('Second took', second_time, 'seconds')
    #
    # print('First was faster by', second_time - first_time, 'seconds')
