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

ENERGY_COST = 0
MAX_BATTERY_CAPACITY = 500  # in kWh
MAX_STOCKAGE_ROOM_LEVEL = 4500
PERCENTAGE_STOCKAGE_ROOM_CHARGE = 100  # in kWh
GRID_POWER = 180  # in kW
swapping_room_slots = [1, 1, 1, 1, 1, 1, 1, 1, 1]
stockage_room_level = MAX_STOCKAGE_ROOM_LEVEL
number_of_battery_charged = 9
df_PV = pd.read_csv("data/df_PV.csv")


def decision_making(env, df_vehicle, arduino):
    global ENERGY_COST
    global number_of_battery_charged
    global PERCENTAGE_STOCKAGE_ROOM_CHARGE

    # Get the current time
    current_time = datetime.utcfromtimestamp(env.now)

    # Check if the current time is a multiple of 30 minutes
    if current_time.minute % 30 == 0 and current_time.second == 0:
        ENERGY_COST += 4
        PERCENTAGE_STOCKAGE_ROOM_CHARGE = (
            round(PERCENTAGE_STOCKAGE_ROOM_CHARGE / 10) * 10
        )
        print(PERCENTAGE_STOCKAGE_ROOM_CHARGE)

        message = "{},{}\n".format(
            number_of_battery_charged, PERCENTAGE_STOCKAGE_ROOM_CHARGE
        )
        arduino.write(message.encode("ascii"))
        # arduino.write(ENERGY_COST.encode("ascii")

        # print("current_time = ", current_time)
        # print("-----------------------------------")
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
        _ = charge_stockage_room(env, pv_power, use_solar_pannel, arduino)
        vehicle_here = 0
        vehicle = df_vehicle[
            df_vehicle["Date Time"] == current_time.strftime("%Y-%m-%d %H:%M:%S")
        ]

        if not vehicle.empty:
            # Charge the vehicle
            vehicle_here = 1
            print("")
            print("")
            print("")
            print("VEHICLE ARRIVES AT", current_time)
            traject = charge_vehicle(env, arduino)
            print("Vehicle", vehicle["Vehicle_ID"].values[0], "is charging")
            # print("charged at", current_time)
            print("")
            print("")

        # CHARGE SWAPPING ROOM

        _ = charge_swapping_room(env, vehicle_here, arduino)


def charge_swapping_room(env, vehicle_here, arduino):
    global swapping_room_slots
    global number_of_battery_charged
    global stockage_room_level
    traject = ""

    if number_of_battery_charged < 9 and vehicle_here == 0:
        for i in range(len(swapping_room_slots)):
            if swapping_room_slots[i] == 0:
                swapping_room_slots[i] = 1
                number_of_battery_charged += 1
            break
        # arduino.write(number_of_battery_charged.encode("ascii"))
        # print("SWAPPING ROOM IS CHARGING ...")
        # print("number_of_battery_charged = ", number_of_battery_charged)
        env.timeout(0.05)
        # )  # assume it is the same charging time for all the batteries

        if stockage_room_level > 1 / 9 * MAX_STOCKAGE_ROOM_LEVEL:  # TO IMPROVE
            # print("ROOM2 --> SWAPPING ROOM ")
            traject = room2_room1
            stockage_room_level -= 500  # 0.5 * GRID_POWER / MAX_STOCKAGE_ROOM_LEVEL
            # print(
            #     "Stockage room is discharging ... level = ", stockage_room_level
            # )  # because we charge every 30 minutes
            env.timeout(0.5)
            PERCENTAGE_STOCKAGE_ROOM_CHARGE = (
                stockage_room_level / MAX_STOCKAGE_ROOM_LEVEL
            )
            # arduino.write(PERCENTAGE_STOCKAGE_ROOM_CHARGE.encode("ascii"))
            # arduino.write(room2_room1.encode("ascii"))

            # arduino.write()
        else:
            traject = grid_room1
            # print("GRID --> SWAPPING ROOM ")
            env.timeout(0.5)
            # arduino.write(grid_room1.encode("ascii"))
    return traject


def charge_stockage_room(env, pv_power, use_solar_pannel, arduino):
    global stockage_room_level
    global PERCENTAGE_STOCKAGE_ROOM_CHARGE
    traject = ""

    if stockage_room_level < MAX_STOCKAGE_ROOM_LEVEL:
        if use_solar_pannel == 0:
            stockage_room_level += min(
                GRID_POWER / 2, MAX_STOCKAGE_ROOM_LEVEL - stockage_room_level
            )

            # because we charge every 30 minutes
            traject = grid_room2
            print("")
            # print(" GRID --> ROOM2 ")
            # print(" Stockage room is charging ... level = ", stockage_room_level)
            env.timeout(0.5)
            PERCENTAGE_STOCKAGE_ROOM_CHARGE = (
                stockage_room_level / MAX_STOCKAGE_ROOM_LEVEL
            )
            # arduino.write(PERCENTAGE_STOCKAGE_ROOM_CHARGE.encode("ascii"))
            # arduino.write(grid_room2.encode("ascii"))
        else:
            stockage_room_level += min(
                pv_power / 2, MAX_STOCKAGE_ROOM_LEVEL - stockage_room_level
            )  # MAX_STOCKAGE_ROOM_LEVEL * 0.5
            # because we charge every 30 minutes
            traject = solar_room2
            # print("")
            # print(" PV --> ROOM2")
            # print(" Stockage room is charging ... level = ", stockage_room_level)
            env.timeout(0.5)
            PERCENTAGE_STOCKAGE_ROOM_CHARGE = (
                stockage_room_level / MAX_STOCKAGE_ROOM_LEVEL
            )
            # arduino.write(PERCENTAGE_STOCKAGE_ROOM_CHARGE.encode("ascii"))
            # arduino.write(solar_room2.encode("ascii"))
    return traject


def charge_vehicle(env, arduino):
    # global number_of_battery_charged
    # global swapping_room_slots
    global number_of_battery_charged
    global stockage_room_level
    global PERCENTAGE_STOCKAGE_ROOM_CHARGE
    # print("-----------------------------------")
    # print("BEFORE CHARGING number_of_battery_charged  = ", number_of_battery_charged)
    # print("BEFORE CHARGING swapping_room_slots = ", swapping_room_slots)
    traject = ""
    if number_of_battery_charged >= 1:
        # print("-----------------------------------")
        # print("SWAPPING ROOM --> VEHICLE ")

        for i in range(len(swapping_room_slots)):
            if swapping_room_slots[i] == 1:
                swapping_room_slots[i] = 0
                number_of_battery_charged -= 1
                break
        # arduino.write(number_of_battery_charged.encode("ascii"))
        # print("AFTER CHARGING number_of_battery_charged = ", number_of_battery_charged)
        # print("AFTER CHARGING swapping_room_slots = ", swapping_room_slots)
    else:
        # print("-----------------------------------")
        # print("CHARGERS --> VEHICLE ")
        if stockage_room_level >= MAX_BATTERY_CAPACITY:
            stockage_room_level -= 500  # (GRID_POWER / MAX_STOCKAGE_ROOM_LEVEL * 30 * 3600)  # because we charge every 30 minutes
            # print("Stockage room is discharging ... level = ", stockage_room_level)
            # print("ROOM2 --> CHARGERS ")
            traject = room2_chargers
            env.timeout(0.5)
            PERCENTAGE_STOCKAGE_ROOM_CHARGE = (
                stockage_room_level / MAX_STOCKAGE_ROOM_LEVEL
            )
            # arduino.write(PERCENTAGE_STOCKAGE_ROOM_CHARGE.encode("ascii"))
            # arduino.write(room2_chargers.encode("ascii"))
        else:
            # print("GRID --> CHARGERS ")
            traject = grid_chargers
            env.timeout(0.5)
            # arduino.write(grid_chargers.encode("ascii"))
    return traject
