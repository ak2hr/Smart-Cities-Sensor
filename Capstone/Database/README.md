Database Conversion library
====================
This repository contains the Database Converstion library, that takes
flood data in two different formats (either csv or a JSON url) and 
inputs it into two different databases (SQLite or InfluxDB). 

The purpose of the scripts contained in this library is to organize and
format flood data collected by sensors and the GPS service Waze. The 
databases can improve accessablility, vizualization, querying, and 
analysis. 

Historical data to SQLite
----------

Data from sesnors that have previously been deployed in Norfolk, VA. and
crowd sourced data from Waze are stored in a CSV. Converting the CSV
to a retational and locally hosted database can facilitate future use cases
by allowing queries on items such as locations or types and a standardization
of the event date. 

SQLite is a locally hosted database, so only those with access to the fdata.db
can utilize it. This allowed for quick and simple construction, and rudimentary 
use cases. In the future it may be nice for the database to be hosted on the 
internet. 

Consideration for the relational database design and the enitity relationship
diagram can be found in the Database Design Pros/Cons PDF.

### datetimeconversion.py

This script reads the flooddata.csv and converts its current fromat to 
datetime format. This is necessary because the database needs a standardized
format for time to allow for future analysis on time series data. 
Datetime format is the most widley used for timeseries data. 

Once the event date is converted to date time, it can either be exported as another 
csv or continued to be used as a Pandas python dataframe for the stacking.py script. 





## Below is from Sean Allen to see format etc.

This library mostly exposes the functions defined by LMIC, it makes no
attempt to wrap them in a higher level API that is more in the Arduino
style. To find out how to use the library itself, see the examples, or
see the PDF file in the doc subdirectory.

This library requires Arduino IDE version 1.6.6 or above, since it
requires C99 mode to be enabled by default.

Installing
----------
To install this library:

 - install it using the Arduino Library manager ("Sketch" -> "Include
   Library" -> "Manage Libraries..."), or
 - download a zipfile from github using the "Download ZIP" button and
   install it using the IDE ("Sketch" -> "Include Library" -> "Add .ZIP
   Library..."
 - clone this git repository into your sketchbook/libraries folder.

For more info, see https://www.arduino.cc/en/Guide/Libraries

Features
--------
The LMIC library provides a fairly complete LoRaWAN Class A and Class B
implementation, supporting the EU-868 and US-915 bands. Only a limited
number of features was tested using this port on Arduino hardware, so be
careful when using any of the untested features.

What certainly works:
 - Sending packets uplink, taking into account duty cycling.
 - Encryption and message integrity checking.
 - Receiving downlink packets in the RX2 window.
 - Custom frequencies and datarate settings.
 - Over-the-air activation (OTAA / joining).

What has not been tested:
 - Receiving downlink packets in the RX1 window.
 - Receiving and processing MAC commands.
 - Class B operation.

If you try one of these untested features and it works, be sure to let
us know (creating a github issue is probably the best way for that).

Configuration
-------------
A number of features can be configured or disabled by editing the
`config.h` file in the library folder. Unfortunately the Arduino
environment does not offer any way to do this (compile-time)
configuration from the sketch, so be careful to recheck your
configuration when you switch between sketches or update the library.

At the very least, you should set the right type of transceiver (SX1272
vs SX1276) in config.h, most other values should be fine at their
defaults.

Supported hardware
------------------
This library is intended to be used with plain LoRa transceivers,
connecting to them using SPI. In particular, the SX1272 and SX1276
families are supported (which should include SX1273, SX1277, SX1278 and
SX1279 which only differ in the available frequencies, bandwidths and
spreading factors). It has been tested with both SX1272 and SX1276
chips, using the Semtech SX1272 evaluation board and the HopeRF RFM92
and RFM95 boards (which supposedly contain an SX1272 and SX1276 chip
respectively).

This library contains a full LoRaWAN stack and is intended to drive
these Transceivers directly. It is *not* intended to be used with
full-stack devices like the Microchip RN2483 and the Embit LR1272E.
These contain a transceiver and microcontroller that implements the
LoRaWAN stack and exposes a high-level serial interface instead of the
low-level SPI transceiver interface.

This library is intended to be used inside the Arduino environment. It
should be architecture-independent, so it should run on "normal" AVR
arduinos, but also on the ARM-based ones, and some success has been seen
running on the ESP8266 board as well. It was tested on the Arduino Uno,
Pinoccio Scout, Teensy LC and 3.x, ESP8266, Arduino 101.

This library an be quite heavy, especially if the fairly small ATmega
328p (such as in the Arduino Uno) is used. In the default configuration,
the available 32K flash space is nearly filled up (this includes some
debug output overhead, though). By disabling some features in `config.h`
(like beacon tracking and ping slots, which are not typically needed),
some space can be freed up. Some work is underway to replace the AES
encryption implementation, which should free up another 8K or so of
flash in the future, making this library feasible to run on a 328p
microcontroller.

Connections
-----------
To make this library work, your Arduino (or whatever Arduino-compatible
board you are using) should be connected to the transceiver. The exact
connections are a bit dependent on the transceiver board and Arduino
used, so this section tries to explain what each connection is for and
in what cases it is (not) required.

Note that the SX1272 module runs at 3.3V and likely does not like 5V on
its pins (though the datasheet is not say anything about this, and my
transceiver did not obviously break after accidentally using 5V I/O for
a few hours). To be safe, make sure to use a level shifter, or an
Arduino running at 3.3V. The Semtech evaluation board has 100 ohm resistors in
series with all data lines that might prevent damage, but I would not
count on that.

### Power
The SX127x transceivers need a supply voltage between 1.8V and 3.9V.
