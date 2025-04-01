import os

from filters.source_filter import read_csv
from filters.transform_filter import transform_data
from filters.pressure_filter import detect_pressure_anomalies, correct_pressure
from filters.temperature_filter import filter_low_temperature
from filters.humidity_filter import filter_humidity_anomalies
from filters.write_filter import write_csv

def main():
    # CSV Input file name
    input_file = "input/sensor_data_550.csv"
    
    # 1) Input filter (source filter)
    data = read_csv(input_file)
    if not data:
        print("No data to process.")
        return
    
    # 2) Convert units (transform filter)
    data = transform_data(data)
    
    # 3) Detect anomalies and correct pressure (pressure filter)
    anomaly_flags, pressure_anomalies_log = detect_pressure_anomalies(data)
    data = correct_pressure(data, anomaly_flags)
    
    # 5) Filter data (temperature and humidity filters)
    low_temp_data = filter_low_temperature(data)
    humidity_anomalies_data = filter_humidity_anomalies(data)
    
    # 4) Output filter (write filter)
    processed_fields = [
        "Timestamp", "Temperature_F", "Temperature_C", "Humidity_Percent",
        "Pressure_hPa", "Corrected_Pressure", "WindSpeed_mph", "WindSpeed_m/s"
    ]
    anomaly_fields = ["Timestamp", "Pressure_hPa", "Previous_Pressure", "Difference"]
    
    os.makedirs("output", exist_ok=True)
    
    write_csv("output/processed_sensor_data.csv", data, processed_fields)
    write_csv("output/pressure_anomalies_log.csv", pressure_anomalies_log, anomaly_fields)
    write_csv("output/low_temperature.csv", low_temp_data, processed_fields)
    write_csv("output/humidity_anomalies.csv", humidity_anomalies_data, processed_fields)
    
    print("Success! Generated output files are in the output/ directory.")

if __name__ == "__main__":
    main()
