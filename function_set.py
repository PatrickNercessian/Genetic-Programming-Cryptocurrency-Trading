# TODO add lists, break/continue keywords
function_set = [
    '+', '-', '*', '/',  # TODO 'pow()',
    'abs(___)', 'sqrt(___)',
    '=',
    '[___]',
    '\n',

    'if ___:', 'elif ___:', 'else:', 'while ___:', 'for ___:',
    'if-elif-block',
    'block',
    'nothing',

    'in',

    '==', '!=', '>=', '<=', '>', '<',
    'and', 'or',
]

unary_operator_type = ['abs(___)', 'sqrt(___)']
binary_operator_type = ['+', '-', '*', '/']  # TODO 'pow()'
assignment_type = ['=']
line_type = ['\n']
if_type = ['if ___:']
while_type = ['while ___:']
# for_type = ['for ___:']
else_type = ['elif ___:', 'else:']
if_elif_block_type = ['if-elif-block']
block_type = ['block']

nothing_type = ['nothing']
# in_type = ['in']
boolean_type = ['==', '!=', '>=', '<=', '>', '<', 'and', 'or']
