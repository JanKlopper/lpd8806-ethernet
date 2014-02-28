#include <EtherCard.h>
#include <EEPROM.h>

const byte
  chipSelect = 8,
  clockPin = 7,
  dataPin = 5,
  frameHeader = 54;
  
  // ethernet interface mac address, must be unique on the LAN
const byte etherMac[6] = {0x74, 0x69, 0x69, 0x2D, 0x30, 0x05};
const char* ledtypes[4] = {"lpd8806", "ws2812", "singlecolor" ,"multicolor"};
const int ledCount = 160;
const byte ledpins[3] = {3, 6, 9}; // 3 single color leds or 1 rgb strip
const byte ver = 1;

const char http_OK[] PROGMEM =
    "HTTP/1.0 200 OK\r\n"
    "Content-Type: text/html\r\n"
    "Pragma: no-cache\r\n\r\n";

// offset addresses for the IP, MAC and led type in the eeprom
const byte eepromIP = 0;
const byte eepromMAC = 4;
const byte eepromLEDType = 10;
byte ledType = 0;
byte ledstep = 0;

// Ethernet buffer receives 3 bytes per LED
// and 54 bytes for the Ethernet frame itself.
byte Ethernet::buffer[ledCount * 3 + frameHeader];
static BufferFiller bfill;

void setup () {
  Serial.begin(57600);
  Serial.println("[ledserver]");
  
  ledType = readLEDType();
  stripSetup(ledType);
  // Set up the ethernet module with our MAC and static IP.
  byte mac[6];
  readMAC(mac);
  if(mac[0] == 0 || mac[0] == 255){
    if (ether.begin(sizeof Ethernet::buffer, etherMac, chipSelect) == 0)
      Serial.println("No eth?");  
    Serial.println("using default mac");
  } else { 
    if (ether.begin(sizeof Ethernet::buffer, mac, chipSelect) == 0)
      Serial.println("No eth?");
    Serial.println("using eeprom mac");
  }
  
  byte etherIP[4];
  readIP(etherIP);
  bool online = false;
  if (etherIP[0] == 0 || etherIP[0] == 255){
    Serial.println("Setting up DHCP");
    if (!ether.dhcpSetup()){
      Serial.println( "DHCP failed");
    } else {
      Serial.print("Online at DHCP:");
      ether.printIp("IP: ", ether.myip);
      online = true;
    }
  }
  if(!online){
    Serial.print("Online at STATIC:");
    ether.staticSetup(etherIP); 
    ether.printIp("IP: ", ether.myip);
  }
  // init led pins as output
  if(ledType > 1){
    for(int i=0; i<sizeof(ledpins); ++i){
      pinMode(ledpins[i], OUTPUT);
    }
  }
}

void loop () {
  // Process incoming packages and color the strip
  word len = ether.packetReceive();
  word pos = ether.packetLoop(len);
  if (pos) {
    bfill = ether.tcpOffset();
    char* data = (char *) Ethernet::buffer + pos;
    Serial.println(data);
    if (strncmp("GET / ", data, 6) == 0){
      // Return home page
      homePage(bfill);      
      ether.httpServerReply(bfill.position());
    } else if (strncmp("POST / ", data, 7) == 0){
      saveConfigPage(data, bfill);    
    } else {
      ledstep = 0;
      len -= frameHeader;
      for (int i = 0; i < len; ++i)
        stripChannelColor(Ethernet::buffer[pos + i]);
      stripLatch(ledType);    
      ether.httpServerReply(0); // Close connection
    } 
  }
}

// eeprom reading and writing
void setIP(byte ip[]){
  Serial.print("IP stored as: ");
  for(int i=0; i<4; ++i){
    EEPROM.write(i+eepromIP, ip[i]);
    Serial.print(ip[i], DEC);
    if (i < 3)
      Serial.print('.');
  }
  Serial.println();
}

void setMAC(byte mac[]){
  Serial.print("MAC stored as: ");
  for(int i=0; i<6; ++i){
    EEPROM.write(i+eepromMAC, mac[i]);
    Serial.print(mac[i], HEX);
    if (i < 5)
      Serial.print(':');
  }
  Serial.println();
}

void setLEDType(int type){
  Serial.print("led type stored as: ");
  EEPROM.write(eepromLEDType, type);
  Serial.println(ledtypes[type]);
}

int readLEDType(){  
  // 0 for lpd8806
  // 1 for WS2812
  // 2 for direct pwm single color pwm / darlington pwm
  // 3 for direct pwm rgb pwm / darlington pwm
  int type = EEPROM.read(eepromLEDType);
  return (type >= sizeof(ledtypes)?0:type);  
}

void readIP(byte ip[]){
  for(int i=0; i<4; ++i){
    ip[i] = EEPROM.read(i+eepromIP);
  }
}

void readMAC(byte mac[]){
  for(int i=0; i<6; ++i){
    mac[i] = EEPROM.read(i+eepromMAC);
  }
}


// webpages//
static void homePage(BufferFiller& buf){
  byte etherIP[4];
  readIP(etherIP);
  byte mac[6];
  readMAC(mac);
  buf.emit_p(PSTR("$F"
                  "<title>LedController: $D</title>"                  
                  "<form method='POST'>"
                  "Ledtype: <select name='type'>"),
             http_OK, 
             ver);     
  // display all available led types
  for(int i=0; i<sizeof(ledtypes); i++){
    buf.emit_p(PSTR("<option value='%D' %S>$S"), 
               i, 
               (readLEDType()==i?"selected":""), 
               ledtypes[i]);
  }
  buf.emit_p(PSTR("</select><br>Ipv4: "));
  // output ipv address octets
  for(int i=0; i<4; i++){
    buf.emit_p(PSTR("<input name='ip%D' value='$D' type='number' min='$D' max='255' maxlength='3'>"), (i+1), etherIP[i], (i==0?1:0));    
  }
  buf.emit_p(PSTR("<br>MAC: "));
  // output ipv address octets
  for(int i=0; i<6; i++){
    buf.emit_p(PSTR("<input name='mac%D' value='$D' type='number' min='0' max='255' maxlength='3'>"), (i+1), mac[i]);    
  }
  
  // show dhcp as enabled based on eeprom value
  buf.emit_p(PSTR("<br>Use DHCP: <input type='checkbox' name='dhcp' value='true' %S>"
                  "<br><input type='submit'></form><br>"
                  "<a href='https://github.com/JanKlopper/lpd8806-ethernet'>Opensource software</a>"),
                  (etherIP[0] == 0 || etherIP[0] == 255?"checked":""));
}

static void saveConfigPage(const char* data, BufferFiller& buf){
  buf.emit_p(PSTR("$F"
                  "<title>LedController v$D</title>"
                  "Config saved"), 
             http_OK, 
             ver);

  char* stringvalue;
  byte value;
  if (ether.findKeyVal(data + 1, stringvalue , 1, "type") > 0) { 
    value = atoi(stringvalue);   // command to convert a string to number
    if ((value >= 0) & (value <= 5)) {
       setLEDType(value);
    }
  }
  
  byte etherIP[4];
  for(int i=0; i<4; i++){
    if (ether.findKeyVal(data + 1, stringvalue , 3 , String("ip"+String(i))) > 0) { 
      value = atoi(stringvalue);   // command to convert a string to number
      if ((value >= 0) & (value <= 255)) {
        etherIP[i] = value;
      }
    }
  }
  setIP(etherIP);
  
  byte mac[6];
  for(int i=0; i<6; i++){
    if (ether.findKeyVal(data + 1, stringvalue , 3 , String("mac"+String(i))) > 0) { 
      value = atoi(stringvalue);   // command to convert a string to number
      if ((value >= 0) & (value <= 255)) {
        mac[i] = value;
      }
    }
  }
  setMAC(mac);  
}

// led strip functions
void stripSetup(int type) {
  // Sets up the LPD8806 Flexistrip
  //
  // Sets data and clock pins to output mode
  // Latches all LPD chips on the strip and then makes them dark.  
  if(type == 0){
    pinMode(dataPin, OUTPUT);
    pinMode(clockPin, OUTPUT);
  
    for (int index = ledCount * 3; index-- > 0;)
      stripLatch(type);
  
    for (int index = ledCount * 3; index-- > 0;)
      stripChannelColor(65);
  }
}

const void stripLatch(int type) {  
  if(type == 0){
    // Latch the LPD8806 strip by sending a byte with a zeroed MSB.
    stripWrite(0);
  }
}

void stripChannelColor(byte level) {
  // Level data is sent as a readable character, starting at 65 instead of 0.
  const byte mask = 128, offset = 65;
  stripWrite(level - offset | mask);
}

void stripWrite(byte data) {
  if(ledType == 0){
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
  } else if(ledType == 1) {
    // ws2801 code should go here
  } else if(ledType == 2) {
    // write out the first color only since we only use one color, ignore the 
    if(ledstep % 3 == 0){
      analogWrite(ledpins[ledstep/3], data*2); // we expect 7 bits data, we feed 8 bits
    }
    ledstep++;
    if (ledstep > sizeof(ledpins)*3)
      ledstep = 0;
  } else if(ledType == 3) {
    analogWrite(ledpins[ledstep], data*2); // we expect 7 bits data, we feed 8 bits
    ledstep++;  
    if (ledstep > sizeof(ledpins))
      ledstep = 0;
  }
}
