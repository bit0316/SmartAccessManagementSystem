import serial

# Arduino serial port
ser = serial.Serial('/dev/ttyACM0', 9600)

# Return parse sensor values
def parse_sensor_values():
    if ser.in_waiting > 0:
        data = ser.readline().strip()
        values = data.decode().split(',')
        pm2p5 = float(values[0])
        pm10 = float(values[1])
        humidity = float(values[2])
        temperature = float(values[3])
        analog_value = int(values[4])
        return pm2p5, pm10, humidity, temperature, analog_value

# Print sensor values
def print_values():
    if ser.in_waiting > 0:
        pm2p5, pm10, humidity, temperature, analog_value = parse_sensor_values()
        print("PM 2.5:", pm2p5)
        print("PM 10:", pm10)
        print("Humidity:", humidity)
        print("Temperature:", temperature)
        print("Analog value:", analog_value)
        print()
