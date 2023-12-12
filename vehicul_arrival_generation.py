import csv
import pandas as pd
from random import randint

# Create a date range for 48 hours with 30-minute intervals starting from December 1st, 2023
date_range = pd.date_range(start="2023-12-01", periods=48 * 2, freq="30T")

# Create a list to hold the randomized vehicle arrival times
data = []

# Generate vehicle arrival times ensuring at least 15 and at most 20 vehicles per day for December 1st and 2nd
for day in ["2023-12-01", "2023-12-02"]:
    vehicles_for_day = randint(40, 50)
    day_indices = date_range[date_range.strftime("%Y-%m-%d") == day].tolist()
    random_indices = [randint(0, len(day_indices) - 1) for _ in range(vehicles_for_day)]
    day_vehicles = [
        (str(day_indices[idx]), "Vehicle Arriving", f"Vehicle_{idx + 1}")
        for idx in random_indices
    ]
    data.extend(day_vehicles)

# Sort data by date time
data.sort(key=lambda x: pd.to_datetime(x[0]))

# Write sorted data to a CSV file
file_path = "data/vehicle_arrival.csv"
with open(file_path, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Date Time", "Vehicle Arrival", "Vehicle_ID"])  # Write header
    writer.writerows(data)  # Write data rows

print(
    f"Randomized, limited, and sorted vehicle arrival planning for 1st and 2nd December 2023 generated and saved to '{file_path}'"
)
