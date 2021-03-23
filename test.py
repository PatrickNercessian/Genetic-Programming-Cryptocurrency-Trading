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


def test1():
    tree = plant_tree(2)
    individual = Individual(tree, 'BTCUSDT', '3m')
    individual.evaluate()
    

def test_plant_tree():
    for i in range(30):
        tree = plant_tree(2)
        print(decode_in_order(tree.root), '\n\n')


def test_crypto_data():
    get_all_crypto_data_online('btc_bars.csv', 'BTCUSDT', '')


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


def test_mutation():
    tree = plant_tree(2)
    indiv = Individual(tree, 'BTCUSDT', '3m')
    mutated_indiv = mutate(indiv)

    print(indiv.code)
    print()
    print(mutated_indiv.code)


def test_crossover():
    tree_1, tree_2 = plant_tree(2), plant_tree(2)
    indiv_1, indiv_2 = Individual(tree_1, 'BTCUSDT', '3m'), Individual(tree_2, 'BTCUSDT', '3m')
    offspring_1, offspring_2 = crossover(indiv_1, indiv_2)

    print(indiv_1.code + '\n\n' + indiv_2.code + '\n\n\n')

    if offspring_1 is not None:
        print(offspring_1.code + '\n\n')
    else:
        print('Crossover for offspring_1 failed... Likely an invalid subtree was placed')

    if offspring_2 is not None:
        print(offspring_2.code)
    else:
        print('Crossover for offspring_2 failed... Likely an invalid subtree was placed')


def test_population():
    population = Population('BTCUSDT', '3m', pop_size=1000)
    population.evaluate_and_sort()
    for i in range(3):
        population.next_gen()
        population.evaluate_and_sort()


# test_tree()
test_population()
