from datetime import datetime, timedelta
import serial
import time
import pandas as pd
import numpy as np
import asyncio


start_time = pd.Timestamp("2023-12-01 00:00:00")
# comport = "/dev/tty.usbserial-1110"  # change with the port u are using
# arduino = serial.Serial(comport, 9600)
# time.sleep(2)
"""
We may add the constants here and do the decision in this section
"""
# Defintion of constants
grid_room1 = "a"
room2_room1 = "b"
grid_room2 = "c"
room2_grid = "d"
solar_room2 = "e"
room2_chargers = "f"
grid_chargers = "h"

MAX_BATTERY_CAPACITY = 500  # in kWh
MAX_STORAGE_ROOM_CAPACITY = 4500  # in kWh
# To use when everything works
electricity_price = pd.read_csv("data/electricity_price.csv")  # in euro/kWh
# Define constants based on assumptions
energy_price_grid = 11  # in ct/kW


def charge_vehicle_with_chargers(
    energy_price_grid,
    stockage_room_level,
    vehicle_battery_capacity,
    energy_cost,
):
    """
    We charge the vehicle with the chargers in the parking:
    Two cases :
        (1) We charge the vehicle with the stockage room (room2) depending on the battery level of room2
        (2) We charge the vehicle with the grid and we pay the energy price

    return : energy trajectory"""
    global MAX_BATTERY_CAPACITY

    if stockage_room_level >= MAX_BATTERY_CAPACITY:
        stockage_room_level -= MAX_BATTERY_CAPACITY
        print(
            "ROOM2 --> CHARGERS / Charging with chargers, current room2 level: ",
            stockage_room_level,
        )
        return room2_chargers, stockage_room_level, energy_cost
    else:
        energy_cost += energy_price_grid * vehicle_battery_capacity / 100
        print("charging with chargers + grid , current energy cost: ", energy_cost)
        return grid_chargers, stockage_room_level, energy_cost


def charge_stockage_room(
    solar_pannel_power,
    energy_price_grid,
    stockage_room_level,
    energy_cost,
):
    """
    We charge the stockage room with the solar pannel or the grid
    return : energy trajectory, stockage_room_level, energy_cost
    """
    global MAX_STORAGE_ROOM_CAPACITY
    # yield env.timeout(1)
    charging_time = 1  # 1h
    if stockage_room_level < MAX_STORAGE_ROOM_CAPACITY:
        if solar_pannel_power > 10:
            trajectory, stockage_room_level = charge_stockage_room_with_solar_pannel(
                solar_pannel_power, stockage_room_level, charging_time
            )
            # arduino.write(trajectory.encode("ascii"))

        else:
            (
                trajectory,
                stockage_room_level,
                energy_cost,
            ) = charge_stockage_room_with_grid(
                energy_price_grid, stockage_room_level, energy_cost
            )
            # arduino.write(trajectory.encode("ascii"))

        return trajectory, stockage_room_level, energy_cost
    else:
        print("No need to charge the stockage room")
        return "No", stockage_room_level, energy_cost


def charge_swapping_room(
    stockage_room_level,
    swapping_room_slots,
    number_of_battery_charged,
    solar_pannel_power,
    energy_cost,
):
    """We charge the swapping room with the stockage room or the grid"""

    if stockage_room_level > 0.2 * MAX_STORAGE_ROOM_CAPACITY:
        (
            traject,
            stockage_room_level,
            number_of_battery_charged,
            swapping_room_slots,
        ) = charge_swapping_with_stockage(
            number_of_battery_charged,
            swapping_room_slots,
            stockage_room_level,
            solar_pannel_power,
            energy_cost,
        )
        # arduino.write(traject.encode("ascii"))
        print("STOCKAGE ROOM --> SWAPPING ROOM")

    else:
        (
            traject,
            number_of_battery_charged,
            swapping_room_slots,
            energy_cost,
        ) = charge_swapping_with_grid(
            number_of_battery_charged,
            swapping_room_slots,
            energy_price_grid,
            stockage_room_level,
            energy_cost,
        )
        # arduino.write(traject.encode("ascii"))
        print("GRID --> SWAPPING ROOM")
    return traject, stockage_room_level, number_of_battery_charged, swapping_room_slots


def charge_stockage_room_with_solar_pannel(
    solar_pannel_power, stockage_room_level, charging_time
):
    """
    We charge the stockage room with the solar pannel ,
      the stockage room level is incremented depending on the charging time
    """
    # yield current_time.timeout(1)
    # # discret event simulation
    stockage_room_level += (
        stockage_room_level
        + solar_pannel_power / MAX_STORAGE_ROOM_CAPACITY * charging_time
    )
    print("solar pannel --> STOCKAGE ROOM, current room2 level: ", stockage_room_level)
    return solar_room2, stockage_room_level


def charge_stockage_room_with_grid(
    energy_price_grid,
    stockage_room_level,
    energy_cost,
):
    """
    We charge the stockage room with the grid
    energy cost is incremented
    """
    # yield current_time.timeout(1)
    while stockage_room_level < MAX_STORAGE_ROOM_CAPACITY:
        energy_cost += energy_price_grid / 100 * 500
        stockage_room_level += 500
    print("GRID --> STORAGE ROOM. Current room level:", stockage_room_level)
    return grid_room2, stockage_room_level, energy_cost


def charge_swapping_with_stockage(
    number_of_battery_charged,
    swapping_room_slots,
    stockage_room_level,
    solar_pannel_power,
    energy_cost,
):
    """
    We charge the swapping room with the stockage room
    return : trajectory, swapping_room_slots, number_of_battery_charged, stockage_room_level
    """
    if number_of_battery_charged < 9:
        number_of_battery_charged += 1
        for i, slot in enumerate(swapping_room_slots):
            if slot == 0:
                swapping_room_slots[i] = 1
        stockage_room_level -= 500
        trajectory, stockage_room_level, energy_cost = charge_stockage_room(
            solar_pannel_power,
            energy_price_grid,
            stockage_room_level,
            energy_cost,
        )
        # arduino.write(trajectory.encode("ascii"))
        print(
            "STOCKAGE_ROOM -> SWAPPING_ROOM, current swapping room level: ",
            swapping_room_slots,
            number_of_battery_charged,
        )

        return (
            room2_room1,
            stockage_room_level,
            number_of_battery_charged,
            swapping_room_slots,
        )
    else:
        print("No need to charge the swapping room with the stockage room")
        return "No", stockage_room_level, number_of_battery_charged, swapping_room_slots


def charge_swapping_with_grid(
    number_of_battery_charged,
    swapping_room_slots,
    energy_price_grid,
    stockage_room_level,
    energy_cost,
):
    """
    We charge the swapping room with the grid"""

    # yield env.timeout(1)
    while number_of_battery_charged < 9:
        energy_cost += energy_price_grid * 100 / 9
        number_of_battery_charged += 1
        for i, slot in enumerate(swapping_room_slots):
            if slot == 0:
                swapping_room_slots[i] = 1
        swapping_room_slots[number_of_battery_charged] = 1
    print(
        "charging swapping room with grid, current swapping room level: ",
        swapping_room_slots,
    )
    return grid_room1, stockage_room_level, number_of_battery_charged, energy_cost


def decision_making(
    env,
    vehicle_arrival_data,
    swapping_room_slots,
    number_of_battery_charged,
    stockage_room_level,
    energy_price_grid,
    vehicle_battery_capacity,
    charging_time,
    energy_cost,
    solar_pannel_power,
    # arduino,
):
    # Define initial battery levels and constraints
    # prendre la valeur dnans le data frame au temps current et check si ya solar energy

    sim_time_datetime = datetime.utcfromtimestamp(env.now)
    if sim_time_datetime.minute % 30 == 0 and sim_time_datetime.second == 0:
        print("env.now", sim_time_datetime)
        arriving_vehicles = vehicle_arrival_data[
            vehicle_arrival_data["Date Time"]
            == sim_time_datetime.strftime("%Y-%m-%d %H:%M:%S")
        ]

        for index, row in vehicle_arrival_data.iterrows():
            vehicle_id = row["Vehicle_ID"]
            arrival_time = row["Date Time"]
            arrival_time = datetime.strptime(arrival_time, "%Y-%m-%d %H:%M:%S")
            # print("sim_time_datetime", sim_time_datetime)
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
                                stockage_room_level,
                                swapping_room_slots,
                                number_of_battery_charged,
                                solar_pannel_power,
                                energy_cost,
                            )

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
