# LPD8806-Ethernet

Control your LPD8806 powered RGB LED-flexistrip over the network.

## Hardware
* Any Arduino or compatible device with at least 1kB RAM (ATmega168 and up)
* LPD8806 RGB flexistrip (SPI, bit-banged)
* ENC28J60 Ethernet module (SPI interface)

## Pin connections
The sketch assumes a certain hardware pin connection. The layout below is based on an Arduino Uno and may be different for other Arduino's (notably, the SPI pins are different on the Leonardo and Mega).

For the ENC28J60 module, connect the following (these are etherCard defaults):
* VCC -> 3.3V
* GND -> GND
* SCK (clock)    -> pin 13 (Hardware SPI clock)
* SO (slave out) -> pin 12 (Hardware SPI master-in)
* SI (slave in)  -> pin 11 (Hardware SPI master-out)
* CS (chip-select) -> pin 8

For the LED-strip:
* Clock -> pin 7
* Data  -> pin 5

The chip-select pin for the ENC28J60 is user configurable, as are the pins for the LED-strip. The other pins are the hardware SPI pins on the Arduino and cannot be changed.

## Libraries
* https://github.com/jcw/ethercard

To keep the memory footprint mimimal, the otherwise fantastic library by Adafruit to control the LPD8806 strip is not used. For all your other projects, you can find this library here: https://github.com/adafruit/LPD8806
