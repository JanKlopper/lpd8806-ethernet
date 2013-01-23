#include <enc28j60.h>
#include <etherShield.h>
#include <ip_arp_udp_tcp.h>
#include <net.h>

#include <LPD8806.h>
#include "SPI.h"


// color strip settings
int dataPin = 8;
int clockPin = 9;
int strandLength = 160;
LPD8806 strip = LPD8806(strandLength, dataPin, clockPin);

// lan module settings
static uint8_t mymac[6] = {0x54,0x55,0x58,0x10,0x00,0x25}; 
static uint8_t myip[4] = {192,168,178,16};
static uint16_t port =80; // listen port for tcp (max range 1-254)

#define BUFFER_SIZE 800
static uint8_t buf[BUFFER_SIZE+1];
#define STR_BUFFER_SIZE 22
static char strbuf[STR_BUFFER_SIZE+1];
EtherShield es=EtherShield();
static boolean debug = false;

void setup(){
  /*initialize enc28j60*/
  es.ES_enc28j60Init(mymac);
  es.ES_enc28j60clkout(2); // change clkout from 6.25MHz to 12.5MHz
  delay(10);
      
  // 0x476 is PHLCON LEDA=links status, LEDB=receive/transmit
  // enc28j60PhyWrite(PHLCON,0b0000 0100 0111 01 10);
  es.ES_enc28j60PhyWrite(PHLCON,0x476);
  //init the ethernet/ip layer:
  es.ES_init_ip_arp_udp_tcp(mymac,myip,port);
  
  Serial.begin(9600);
  Serial.println("init LDP8806 lan controller");
  
  // Init the lightstrip
  strip.begin();
  // Update the strip, to start they are all 'off'
  strip.show();
}

void loop() {
  uint16_t plen, dat_p;
  plen = es.ES_enc28j60PacketReceive(BUFFER_SIZE, buf);
  //plen will ne unequal to zero if there is a valid packet (without crc error) 
  if(plen!=0){
    // arp is broadcast if unknown but a host may also verify the mac address by sending it to a unicast address.
    if(es.ES_eth_type_is_arp_and_my_ip(buf,plen)){
      es.ES_make_arp_answer_from_request(buf);
      return;
    }

    // check if ip packets are for us:
    if(es.ES_eth_type_is_ip_and_my_ip(buf,plen)==0){
      return;
    }

    if(buf[IP_PROTO_P]==IP_PROTO_ICMP_V && buf[ICMP_TYPE_P]==ICMP_TYPE_ECHOREQUEST_V){
      es.ES_make_echo_reply_from_request(buf,plen);
      return;
    }
    
    // tcp port www start, compare only the lower byte
    if (buf[IP_PROTO_P]==IP_PROTO_TCP_V &&
        buf[TCP_DST_PORT_H_P]==0 &&
        buf[TCP_DST_PORT_L_P]==port){
      if (buf[TCP_FLAGS_P] & TCP_FLAGS_SYN_V){
         es.ES_make_tcp_synack_from_syn(buf); // make_tcp_synack_from_syn does already send the syn,ack
         return;     
      }

      if (buf[TCP_FLAGS_P] & TCP_FLAGS_ACK_V){
        es.ES_init_len_info(buf); // init some data structures
        dat_p=es.ES_get_tcp_data_pointer();

        if (dat_p==0){ // we can possibly have no data, just ack:
          if (buf[TCP_FLAGS_P] & TCP_FLAGS_FIN_V){
            es.ES_make_tcp_ack_from_any(buf);
          }
          return;
        }

        uint16_t i=0;
        boolean run = true;
        while(run){
          if(buf[dat_p+i] != NULL && !(buf[dat_p+i] == 13 || 
                                       buf[dat_p+i] == 10)){
            //Serial.write(buf[dat_p+i]);
            if(debug){
              Serial.print(buf[dat_p+i] - 65, DEC);
              Serial.print(buf[dat_p+i+1] - 65, DEC);
              Serial.print(buf[dat_p+i+2] - 65, DEC);
              Serial.write("\n\r");
            }
            strip.setPixelColor(i/3, strip.Color(buf[dat_p+i] - 65,
                                               buf[dat_p+i+1] - 65,
                                               buf[dat_p+i+2] - 65));
            i = i+3;
          } else {
            if(debug){ Serial.println("end of command"); }
            run = false;
          }          
        }
        uint16_t remainleds;
        for(remainleds = i/3; remainleds < strandLength; remainleds++){
          strip.setPixelColor(remainleds, strip.Color(0,0,0));
        }
        strip.show();
        
        plen=es.ES_fill_tcp_data_p(buf,0,PSTR("ktnhxbye"));
        es.ES_make_tcp_ack_from_any(buf); // send ack for http get
        es.ES_make_tcp_ack_with_data(buf,plen); // send data       
        
      }
    }
  }  
}
