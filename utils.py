import random, string

def generate_session_id(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(length))
