# LPD8806-Ethernet

Control your LPD8806 powered RGB flexistrip over the network.

## Hardware
* LPD8806 RGB flexistrip (SPI, bit-banged)
* ENC28J60 Ethernet module (SPI interface)

## Libraries
* Arduino SPI
* https://github.com/jcw/ethercard

To keep the memory footprint mimimal, the otherwise fantastic library by Adafruit to control the LPD8806 strip is not used. For all your other projects, you can find this library here: https://github.com/adafruit/LPD8806
