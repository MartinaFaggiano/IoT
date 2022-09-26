import time
import Adafruit_BMP.BMP085 as BMP085
import Adafruit_DHT

def measure():

    sensor2 = BMP085.BMP085()
    sensor3 = Adafruit_DHT.DHT11
    pin = 4

    while True:

        humidity, temp = Adafruit_DHT.read_retry(sensor3, pin)
        time.sleep(1)
        temperature = sensor2.read_temperature()
        pressure =  sensor2.read_pressure()

        return temperature, pressure, humidity

# if __name__ == "__main__":
#     temp = measure()
#     print (temp)