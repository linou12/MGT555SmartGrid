# Smart Grid Simulation
import cProfile
import serial
import time
import simpy
import simpy.rt
import pandas as pd
from helper import *

# Initialize the serial connection
# comport = "/dev/tty.usbserial-110"  # change with the port u are using
# arduino = serial.Serial(comport, 9600)
# time.sleep(2)

# Define the different energy trajectories as constants
grid_room1 = "a"
room1_room2 = "b"
grid_room2 = "c"
room2_grid = "d"
solar_room2 = "e"
room2_chargers = "f"
grid_chargers = "h"


# Vehicle battery level
# Energy price as a constant per hour


i = 0

# read vehicul arrival data
file_path = "data/vehicle_arrival.csv"
df_vehicle = pd.read_csv(file_path)
time_scaling_factor = 200 / (48 * 3600)
start_time = pd.Timestamp("2023-12-01 00:00:00")
# Initialize the simulation environment with the specified start time
env = simpy.rt.RealtimeEnvironment(
    initial_time=start_time.timestamp(), factor=time_scaling_factor, strict=False
)
swapping_room_slots = [1, 1, 1, 1, 1, 1, 1, 1, 1]
number_of_battery_charged = 9
vehicle_battery_capacity = 500  # in kWh
stockage_room_level = 4500  # Room 2 battery level in percentage
charger_power = 150  # in kW
charging_time = vehicle_battery_capacity / charger_power
energy_price_grid = 11  # in ct/kWh
# Define the energy cost as a global variable it will be incremented if we charge with the grid
energy_cost = 0
solar_pannel_power = 0

simulation_duration = 48 * 3600 + env.now


def my_simulation():
    time.sleep(0.02)
    while env.now < simulation_duration:
        decision_making(
            env,
            df_vehicle,
            swapping_room_slots,
            number_of_battery_charged,
            stockage_room_level,
            energy_price_grid,
            vehicle_battery_capacity,
            charging_time,
            energy_cost,
            solar_pannel_power,
            # arduino,
        )

        yield env.timeout(2)

    # Start the simulation with all the battery fully charged


# in seconds
env.process(my_simulation())
cProfile.run("my_simulation()")  # Run the simulation for a full day
env.run(
    until=simulation_duration
)  # Run the simulation for a full day (24 hours * 3600 seconds)


# Close the serial connection
# arduino.close()
print("connection closed")
# Close the serial connection
