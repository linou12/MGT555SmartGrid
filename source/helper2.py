from datetime import datetime, timedelta
import pandas as pd
import numpy as np

start_time = pd.Timestamp("2023-12-01 00:00:00")
# Constants for Arduino
grid_room1 = "a"
room2_room1 = "b"
grid_room2 = "c"
room2_grid = "d"
solar_room2 = "e"
room2_chargers = "f"
grid_chargers = "h"

MAX_BATTERY_CAPACITY = 500  # in kWh
MAX_STOCKAGE_ROOM_LEVEL = 4500  # in kWh
GRID_POWER = 180  # in kW
swapping_room_slots = [1, 1, 1, 1, 1, 1, 1, 1, 1]
stockage_room_level = MAX_STOCKAGE_ROOM_LEVEL
number_of_battery_charged = 9
df_PV = pd.read_csv("data/df_PV.csv")


def decision_making(env, df_vehicle):
    # Get the current time
    current_time = datetime.utcfromtimestamp(env.now)

    # Check if the current time is a multiple of 30 minutes
    if current_time.minute % 30 == 0 and current_time.second == 0:
        print("current_time = ", current_time)
        # CHARGE STOCKAGE ROOM
        solar_pannel_power = df_PV[
            df_PV["DateTime"] == current_time.strftime("%Y-%m-%d %H:%M:%S")
        ]
        use_solar_pannel = 0
        if solar_pannel_power.empty:
            pv_power = 0
        else:
            pv_power = solar_pannel_power["Power"].values[0]
        if pv_power > 100:
            use_solar_pannel = 1
        _ = charge_stockage_room(env, pv_power, use_solar_pannel)
        vehicle_here = 0
        vehicle = df_vehicle[
            df_vehicle["Date Time"] == current_time.strftime("%Y-%m-%d %H:%M:%S")
        ]

        if not vehicle.empty:
            # Charge the vehicle
            vehicle_here = 1
            traject = charge_vehicle(env)
            print("Vehicle", vehicle["Vehicle_ID"].values[0], "is charging")
            print("charged at", current_time)

        # CHARGE SWAPPING ROOM

        _ = charge_swapping_room(env, vehicle_here)


def charge_swapping_room(env, vehicle_here):
    global swapping_room_slots
    global number_of_battery_charged

    if number_of_battery_charged < 9 and vehicle_here == 0:
        for i in range(len(swapping_room_slots)):
            if swapping_room_slots[i] == 1:
                swapping_room_slots[i] = 0
                number_of_battery_charged -= 1
                # yield env.timeout(
                #     0.05
                # )  # assume it is the same charging time for all the batteries

        if (
            stockage_room_level
            > number_of_battery_charged / 9 * MAX_STOCKAGE_ROOM_LEVEL
        ):  # TO IMPROVE
            print("ROOM2 --> SWAPPING ROOM at {}".format(env))
            stockage_room_level -= 0.5 * GRID_POWER / MAX_STOCKAGE_ROOM_LEVEL
            print(
                "Stockage room is discharging ... level = ", stockage_room_level
            )  # because we charge every 30 minutes
            yield env.timeout(0.5)
            # arduino.write(room2_room1.encode("ascii"))
        else:
            print("GRID --> SWAPPING ROOM at {}".format(env))
            yield env.timeout(0.5)
            # arduino.write(grid_room1.encode("ascii"))


def charge_stockage_room(env, pv_power, use_solar_pannel):
    global stockage_room_level

    if stockage_room_level < MAX_STOCKAGE_ROOM_LEVEL:
        if use_solar_pannel == 0:
            stockage_room_level += (
                GRID_POWER / MAX_STOCKAGE_ROOM_LEVEL * 0.5
            )  # because we charge every 30 minutes
            print(" GRID --> ROOM2 at {}".format(env))
            yield env.timeout(1)
            # arduino.write(grid_room2.encode("ascii"))
        else:
            stockage_room_level += pv_power / MAX_STOCKAGE_ROOM_LEVEL * 0.5
            # because we charge every 30 minutes
            print(" PV --> ROOM2 at {}".format(env))
            yield env.timeout(1)
            # arduino.write(solar_room2.encode("ascii"))


def charge_vehicle(env):
    # global number_of_battery_charged
    # global swapping_room_slots
    global number_of_battery_charged
    global stockage_room_level

    print("number_of_battery_charged = ", number_of_battery_charged)
    print("swapping_room_slots = ", swapping_room_slots)
    traject = ""
    if number_of_battery_charged > 1:
        print("SWAPPING ROOM --> VEHICLE at {}".format(env))
        print("number_of_battery_charged = ", number_of_battery_charged)
        print("swapping_room_slots = ", swapping_room_slots)
        for i in range(len(swapping_room_slots)):
            if swapping_room_slots[i] == 1:
                swapping_room_slots[i] = 0
                number_of_battery_charged -= 1
                break

    else:
        print("CHARGERS --> VEHICLE at {}".format(env))
        if stockage_room_level >= MAX_BATTERY_CAPACITY:
            stockage_room_level -= (
                GRID_POWER / MAX_STOCKAGE_ROOM_LEVEL * 0.5
            )  # because we charge every 30 minutes
            print("Stockage room is discharging ... level = ", stockage_room_level)
            traject = "ROOM2 --> CHARGERS"
            # yield env.timeout(1)
            # arduino.write(room2_chargers.encode("ascii"))
        else:
            traject = "ROOM2 --> CHARGERS"
            # yield env.timeout(1)
            # arduino.write(grid_chargers.encode("ascii"))
    return traject
