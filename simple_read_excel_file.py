import os # For file path operations
import pandas as pd   # For reading Excel file

excel_path = os.path.join(os.path.dirname(__file__), 'databases', 'database_test_PV_Power.csv')

def get_PV_data(excel_path):
    # Load solar power data from Excel file using Pandas
    # df_PV = pd.read_csv(excel_path, skiprows = 1, decimal=',', index_col= ['time'], delimiter = ';', names=['time', 'Power'])
    df_PV = pd.read_csv(excel_path, delimiter=';', decimal=',', names=['time', 'Power'], header=0, skipfooter=1)
    return df_PV

def main():
    # e.g print the dataframe
    df_PV = get_PV_data(excel_path)
    print(f"\n first 15 lines are \n{df_PV.head(15)}\n")

    # e.g print specific row
    row = df_PV.loc[5]
    print(f"the 5th row is:\n{row}\n")

    # # e.g print rows where power is greater than 40 kW
    high_power_rows = df_PV[df_PV['Power'] > 400]
    print(f"the hours with more than 400kW  of power are:\n{high_power_rows}\n")

if __name__ == "__main__":
    main()