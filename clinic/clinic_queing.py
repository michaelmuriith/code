import numpy as np
import simpy

def generate_inter_arrival():
    return np.random.exponential(1./4.0)

def generate_service():
    return np.random.exponential(1./2.0)

def clinic_run(env, servers):
    i = 0
    while True:
        i += 1
        yield env.timeout(generate_inter_arrival())
        env.process(customer(env, i, servers))

wait_t = []

def customer(env, customer, servers):
    with servers.request() as request:
        t_arrival = env.now
        print( env.now, ' customer {} arrives'.format(customer))
        yield request
        print( env.now, ' customer {} is being served'.format(customer))
        yield env.timeout(generate_service())
        print( env.now, ' customer {} departs'.format(customer))
        t_depart = env.now
        wait_t.append(t_depart - t_arrival)



np.random.seed(0)

env = simpy.Environment()

servers = simpy.Resource(env, capacity=1)

env.process(clinic_run(env, servers))


env.run(until=300)
