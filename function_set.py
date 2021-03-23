# TODO add lists, break/continue keywords
function_set = [
    '+', '-', '*', '/',  # TODO 'pow()',
    'abs()', 'sqrt()',
    '=',
    '[]',
    '\n', '\nend-block',

    ':',
    'if', 'while',

    'for',
    'in',

    '==', '!=', '>=', '<=', '>', '<',
    'and', 'or',
]

unary_operator_type = ['abs()', 'sqrt()']
binary_operator_type = ['+', '-', '*', '/']  # TODO 'pow()'
assignment_type = ['=']
line_type = ['\n', '\nend-block', ':']
block_type = ['if', 'while', 'for']
in_type = ['in']
boolean_type = ['==', '!=', '>=', '<=', '>', '<', 'and', 'or']
