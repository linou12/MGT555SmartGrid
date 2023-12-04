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
time_scaling_factor = 480 / (48 * 3600)
start_time = pd.Timestamp("2023-12-01 00:00:00")
# Initialize the simulation environment with the specified start time
env = simpy.rt.RealtimeEnvironment(
    initial_time=start_time.timestamp(), factor=time_scaling_factor
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
solar_pannel_power = 10


def my_simulation():
    while env.now < simulation_duration:
        sim_time_datetime = datetime.utcfromtimestamp(env.now)
        if sim_time_datetime.minute % 30 == 0 and sim_time_datetime.second == 0:
            print("env.now", sim_time_datetime)
            # for i in range(5):
            # arduino.write(grid_room1.encode("ascii"))
            # time.sleep(0.002)
            # arduino.write(room2_room1.encode("ascii"))
            # time.sleep(0.002)
            # arduino.write(grid_chargers.encode("ascii"))
            # time.sleep(0.000002)
            # arduino.write(solar_room2.encode("ascii"))
            # time.sleep(0.000002)
            # arduino.write(room2_chargers.encode("ascii"))
            # time.sleep(0.000002)
            # arduino.write(grid_room2.encode("ascii"))
            # time.sleep(0.000002)
            # arduino.write(room2_grid.encode("ascii"))
            # Defintion of constants
            threshold_pannel_power = 100

            for index, row in df_vehicle.iterrows():
                vehicle_id = row["Vehicle_ID"]
                arrival_time = row["Date Time"]
                arrival_time = datetime.strptime(arrival_time, "%Y-%m-%d %H:%M:%S")
                print("sim_time_datetime", sim_time_datetime)
                if arrival_time == sim_time_datetime:
                    print("arrival time", arrival_time)
                    print("current time", sim_time_datetime)
                    # Compare the arrival time in the dataset with the current simulation time
                    if number_of_battery_charged > 0:
                        for i, slot in enumerate(swapping_room_slots):
                            if slot == 1:
                                swapping_room_slots[i] = 0
                                number_of_battery_charged -= 1
                                print("charging with swapping room")
                                (
                                    traject,
                                    stockage_room_level,
                                    number_of_battery_charged,
                                    swapping_room_slots,
                                ) = charge_swapping_room(
                                    env,
                                    stockage_room_level,
                                    swapping_room_slots,
                                    number_of_battery_charged,
                                    solar_pannel_power,
                                    threshold_pannel_power,
                                    charging_time,
                                    energy_cost,
                                )
                                yield env.timeout(1 * time_scaling_factor)

                                print("charging with swapping room")
                                break
                    else:
                        charge_vehicle_with_chargers(
                            env,
                            energy_price_grid,
                            stockage_room_level,
                            vehicle_battery_capacity,
                            charging_time,
                            energy_cost,
                        )
                        print("charging with chargers")
                    # return swapping_room_slots, number_of_battery_charged

                    # arduino.write(grid_room1.encode("ascii"))
                    # time.sleep(0.000002)
                    # arduino.write(room2_room1.encode("ascii"))
                    # time.sleep(0.000002)
                    # arduino.write(grid_chargers.encode("ascii"))
                    # time.sleep(0.000002)
                    print("charging vehicle", vehicle_id)

        yield env.timeout(15)

    # Start the simulation with all the battery fully charged


simulation_duration = 48 * 3600 + env.now
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
