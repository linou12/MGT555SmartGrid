import random
import simpy
import numpy as np


from helper import *

MAX_VEHICLES = 40
AVG_CHARGING_TIME = 60  # minutes
SIM_TIME = 48 * 60  # minutes
ARRIVAL_INTERVAL = 30  # minutes


class Station:
    def __init__(self, env, max_vehicles, charging_time):
        self.env = env
        self.charger = simpy.Resource(env, max_vehicles)
        self.charging_time = charging_time

    def charge(self, vehicle):
        yield self.env.timeout(self.charging_time)
        print("Vehicle {} charged at {}".format(vehicle, self.env.now))

    def vehicle(env, name, station):
        print("Vehicle {} arriving at charging station at {}".format(name, env.now))
        with station.charger.request() as req:
            yield req
            print("Vehicle {} starting to charge at {}".format(name, env.now))
            yield env.process(station.charge(name))
            print("Vehicle {} leaving the station at {}".format(name, env.now))


# generates random vehicles arrival
def vehicle_generator(env, station):
    for vehicle_id in range(1, MAX_VEHICLES + 1):
        yield env.timeout(
            random.expovariate(1.0 / 10)
        )  # Example: Poisson arrival with mean rate of 10 per time unit
        env.process(vehicle(env, f"Vehicle {vehicle_id}", station))


def vehicle(env, name, station):
    print(f"Vehicle {name} arriving at charging station at {env.now:.2f}")
    with station.charger.request() as req:
        yield req
        print(f"Vehicle {name} starting to charge at {env.now:.2f}")
        yield env.process(station.charge(name))
        print(f"Vehicle {name} leaving the station at {env.now:.2f}")


def setup(env, max_vehicles, charging_time, arrival_interval):
    station = Station(env, max_vehicles, charging_time)
    for i in range(max_vehicles):
        env.process(vehicle(env, i, station))
        while i < MAX_VEHICLES:
            yield env.timeout(
                random.randint(arrival_interval - 2, arrival_interval + 2)
            )
            env.process(vehicle(env, f"Vehicle {i}", station))
            i += 1


print("Starting station simpulation")
env = simpy.Environment()
env.process(setup(env, MAX_VEHICLES, AVG_CHARGING_TIME, ARRIVAL_INTERVAL))
env.run(until=SIM_TIME)
