#include <EtherCard.h>

const byte
  chipSelect = 8,
  clockPin = 7,
  dataPin = 5,
  frameHeader = 54,
  // ethernet interface mac address, must be unique on the LAN
  etherMac[] = {0x74, 0x69, 0x69, 0x2D, 0x30, 0x31},
  etherIP[] = {192, 168, 178, 16};
const int ledCount = 160;
// Ethernet buffer receives 3 bytes per LED
// and 54 bytes for the Ethernet frame itself.
byte Ethernet::buffer[ledCount * 3 + frameHeader];
BufferFiller bfill;

void setup () {
  Serial.begin(57600);
  Serial.println("[MINISERVER]");
  stripSetup();
  // Set up the ethernet module with our MAC and static IP.
  if (ether.begin(sizeof Ethernet::buffer, etherMac) == 0, chipSelect)
    Serial.println("No eth?");
  ether.staticSetup(etherIP); 
}

void loop () {
  // Process incoming packages and color the strip
  int len = ether.packetReceive();
  int pos = ether.packetLoop(len);
  if (pos) {
    len -= frameHeader;
    for (int i = 0; i < len; ++i)
      stripChannelColor(Ethernet::buffer[pos + i]);
    stripLatch();
    ether.httpServerReply(0); // Close connection
  }
}

void stripSetup() {
  // Sets up the LPD8806 Flexistrip
  //
  // Sets data and clock pins to output mode
  // Latches all LPD chips on the strip and then makes them dark.  
  pinMode(dataPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
  for (int index = ledCount * 3; index-- > 0;)
    stripLatch();
  for (int index = ledCount * 3; index-- > 0;)
    stripChannelColor(65);
}

const void stripLatch(void) {
  // Latch the LPD8806 strip by sending a byte with a zeroed MSB.
  stripWrite(0);
}

void stripChannelColor(byte level) {
  // Level data is sent as a readable character, starting at 65 instead of 0.
  const byte mask = 128, offset = 65;
  stripWrite(level - offset | mask);
}

void stripWrite(byte data) {
  // Write a byte to the LPD8806 Flexistrip using bitbanging.
  // This specific code is taken from the LPD8806 libary by Adafruit.
  const byte
    clkPinMask = digitalPinToBitMask(clockPin),
    dataPinMask = digitalPinToBitMask(dataPin);
  volatile byte
    *clkPort = portOutputRegister(digitalPinToPort(clockPin)),
    *dataPort = portOutputRegister(digitalPinToPort(dataPin));
  for(byte bit = 0x80; bit; bit >>= 1) {
    if (data & bit)
      *dataPort |=  dataPinMask;
    else
      *dataPort &= ~dataPinMask;
    *clkPort |=  clkPinMask;
    *clkPort &= ~clkPinMask;
  }
}
