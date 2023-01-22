import Adafruit_DHT

# Sensor should be set to Adafruit_DHT.DHT11,
# Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
sensor = Adafruit_DHT.DHT11

# Example using a Raspberry Pi with DHT sensor
# connected to GPIO23.
pin = 25

# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
def get_humidity():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    return humidity

# Note that sometimes you won't get a reading and
# the results will be null (because Linux can't
# guarantee the timing of calls to read the sensor).
# If this happens try again!

def main():
    humidity = get_humidity()
    if humidity is not None:
        print(f'Humidity={humidity:0.1f}%')
    else:
        print('Failed to get reading. Try again!')

if __name__ == '__main__':
    main()
