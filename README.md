# Smart-Cities-Sensor
Git repo for the second version of the Smart Cities floodwater measurement system.

Code for the original proejct can be found in the [Legacy System folder](https://github.com/UVAdMIST/stormwater-iot).

# How it Works

The device works by taking measurements with the ultrasonic sensor which are posted to the cloud every minute. A measurement is compiled by averaging readings over the span of a minute, removing any notable deviations from what could be considered a "realistic" measurement (e.g. if someone stands under the sensor for a minute, we know flood water doesn't rise six feet that quickly). Measurements are then compared against a baseline reading which was collected at installation, prefereably on a sunny day, to determine whether or not an area should be deemed "flooded".

Measurements are stored as persistent data by being transmitted via the Things Network to a Heroku web app at a static URL. This web app pasrses the data being transmitted from the Things Network and creates a simple JSON data point of the last reading. The Systems side of this project pulls the JSON output from the webpage, and inserts the relevant information into an InfluxDb instance which holds and displays the data for an extended period of time.

The hardware is housed in an electrical components box so that it is fully waterproof. A rubber mat on the back of the box is used to create friction between the device and the pole to which it is mounted so that the device remains firmly in place once strapped on.


# Hardware Used
- [Things Uno](https://www.thethingsnetwork.org/docs/devices/uno/) - Microcontroller used to transmit sensor readings to the Things Network.
- [Maxbotix MB7092](https://www.maxbotix.com/Ultrasonic_Sensors/MB7092.htm) - Ultrasonic sensor used to monitor rising flood levels.
- [Large 6V 3.5W Solar Panel](https://www.adafruit.com/product/500) - Renewable source of energy for prolonged operation of each device.
- [VERTER 5V USB Buck-Boost](https://www.adafruit.com/product/2190) - Boosts the solar panel's voltage output.
- [Solar Lithium Ion Charger](https://www.adafruit.com/?q=USB%2FDC%2FSolar%20Lithium%20Ion%2FPolymer%20Charger) - Converter from the Solar Panel to the battery.

# Software Used
- [The Things Network](thethingsnetwork.com) - IOT-based service to collect data and transfer to a static database.
- [Heroku] (TODO: ADD HOSTING SITE) - Static URL for active display of recent data readings.
- [Arduino IDE] (https://www.arduino.cc/en/Main/Software) - The Things Uno makes use of Arduino's IDE to connect to your computer and download your code. This IDE will be necessary to communicate with the sensor's microcontroller.

# Ideas for Future Development
- Refine data cleaning algorithm to more reliably remove outliers or inaccurate measurements.
- Add more sensors to account for ambient conditions so that flooding risk factors can be determined.
- Build a text messaging alert system to notify residents when a specific area is at risk of flooding.
