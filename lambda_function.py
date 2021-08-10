import test

def lambda_handler(event, context):
    gen_code = test.test_population()

    # message = 'Hello {} {}!'.format(event['first_name'], event['last_name'])
    return {
        'gen_code': gen_code
    }