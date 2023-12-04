# Smart Grid Simulation
import serial
import time
import simpy
import simpy.rt
import pandas as pd
from source.helper import *

# Initialize the serial connection
# comport = "/dev/tty.usbserial-1110"  # change with the port u are using
# arduino = serial.Serial(comport, 9600)
# time.sleep(2)

# Define the different energy trajectories as constants
grid_room1 = "gR1"
room1_room2 = "R2R1"
grid_room2 = "gR2"
room2_grid = "R2g"
solar_room2 = "SR2"
room2_chargers = "R2C"
chargers_grid = "CR2g"
grid_chargers = "gCR2"


# Define initial battery levels and constraints
room1_battery_level = 100  # Room 1 battery level in percentage
room2_battery_level = 100  # Room 2 battery level in percentage
# Define constants based on assumptions
threshold_room1_low = 10  # Threshold for low battery level in Room 1
threshold_room2_low = 10  # Threshold for low battery level in Room 2
# Vehicle battery level
vehicle_battery_level = 10  # Vehicle battery level in percentage
# Energy price as a constant per hour
energy_price_grid = 0.2  # in euro/kWh

i = 0

# read vehicul arrival data
file_path = "data/vehicle_arrival.csv"
df_vehicle = pd.read_csv(file_path)
time_scaling_factor = 480 / (48 * 3600)
start_time = pd.Timestamp("2023-12-01 00:00:00")
# Initialize the simulation environment with the specified start time
env = simpy.rt.RealtimeEnvironment(
    initial_time=start_time.timestamp(), factor=time_scaling_factor
)
swapping_room_slots = [1, 1, 1, 1, 1, 1, 1, 1, 1]
number_of_battery_charged = 9
vehicle_battery_capacity = 500  # in kWh
stockage_room_level = 100  # Room 2 battery level in percentage
charger_power = 150  # in kW
charging_time = vehicle_battery_capacity / charger_power
# Define the energy cost as a global variable it will be incremented if we charge with the grid
energy_cost = 0
solar_pannel_power = 0


def my_simulation():
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
        )
        yield env.timeout(5)

    # Start the simulation with all the battery fully charged


simulation_duration = 48 * 3600 + env.now
# in seconds
env.process(my_simulation())  # Run the simulation for a full day
env.run(
    until=simulation_duration
)  # Run the simulation for a full day (24 hours * 3600 seconds)


# Close the serial connection
# arduino.close()
# print("connection closed")
# Close the serial connection