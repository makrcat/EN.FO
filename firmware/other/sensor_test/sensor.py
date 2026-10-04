import time
import busio
import board
import adafruit_bme680

i2c_sensor = busio.I2C(
        scl=board.D5,
        sda=board.D4,
        frequency=100_000
    ) #400

bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c_sensor, address=0x77) 
reading_interval = 3
max_gas_resistance = 0


# Flag to skip the very first initial junk reading
first_run = True

while True:
    current_gas = bme680.gas
    
    if first_run:
        # Ignore this first data point and lower the flag
        first_run = False
        time.sleep(reading_interval)
        continue
    
    # Update the maximum if the current reading is higher
    if current_gas > max_gas_resistance:
        max_gas_resistance = current_gas
        
    print(f"Current: {current_gas:<8} ohms | Max Baseline: {max_gas_resistance:<8} ohms")
    time.sleep(reading_interval)
