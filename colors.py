#!/usr/bin/python
"""ledstrip trough telnet-interface"""
import telnetlib
import time
import random


# Slightly different, this one makes the rainbow wheel equally distributed
# along the chain
def RainbowCycle(strip):
  for j in xrange(383*5): #5 cycles of all 384 colors in the wheel
    for i in xrange(strip.led_count):
      # tricky math! we use each pixel as a fraction of the full 384-color wheel
      # (thats the i / strip.led_count() part)
      # Then add in j which makes the colors go around per pixel
      # the % 384 is to make the wheel cycle around
      colors = Wheel( ((i * 384 / strip.led_count) + j) % 384)
      strip.setPixelColor(i, *colors)
    strip.show() # write all the pixels out

def Disco(strip, colors, segments, delay):
  segmentlength = strip.led_count / segments
  for i in xrange(strip.led_count):
    if i % segmentlength == 0:
      color = random.choice(colors)
    strip.setPixelColor(i, *color)
  strip.show()
  time.sleep(delay)

def colorWipe(strip, r, g, b):
  for i in xrange(strip.led_count):
    strip.setPixelColor(i, r, g, b)
    strip.show()
    time.sleep(.2)

def colorChase(strip, r, g, b):
  # Chase one dot down the full strip.

  # Start by turning all pixels off:
  for i in xrange(strip.led_count):
    strip.setPixelColor(i, 0, 0, 0)

  # Then display one pixel at a time:
  for i in xrange(strip.led_count):
    strip.setPixelColor(i, r, g, b) # Set new pixel 'on'
    strip.show()                  # Refresh LED states
    strip.setPixelColor(i, 0, 0, 0) # Erase pixel, but don't refresh!
    time.sleep(.2)
  strip.show() # Refresh to turn off last pixel


def rainbow(strip):
  for j in xrange(384): # 3 cycles of all 384 colors in the wheel
    for i in xrange(strip.led_count):
      colors = Wheel((i + j) % 384)
      strip.setPixelColor(i, *colors)
    strip.show()

def Wheel(WheelPos):
  if WheelPos / 128 == 0:
    r = 127 - WheelPos % 128    # Red down
    g = WheelPos % 128          # Green up
    b = 0                       # blue off
  elif WheelPos / 128 == 1:
    g = 127 - WheelPos % 128    # green down
    b = WheelPos % 128          # blue up
    r = 0                       #red off
  elif WheelPos / 128 == 2:
    b = 127 - WheelPos % 128    # blue down
    r = WheelPos % 128          # red up
    g = 0                       # green off
  return r, g, b

class LPD8806(object):

  def __init__(self, host, port, led_count):
    self.host = host
    self.port = port
    self.led_count = led_count
    self.leds = {}

  def setPixelColor(self, led, r, g, b):
    self.leds[led] = (r, g, b)

  def show(self):
    output = []
    try:
      for led in xrange(self.led_count):
        output.append(chr(self.leds[led][0] + 65))
        output.append(chr(self.leds[led][1] + 65))
        output.append(chr(self.leds[led][2] + 65))
        print (chr(self.leds[led][0] + 65) +
               chr(self.leds[led][1] + 65) +
               chr(self.leds[led][2] + 65))
    except KeyError:
      output.append('AAA')

    t = telnetlib.Telnet(self.host, self.port)
    t.write(''.join(output))
    t.close()


def ForeverRainbows(host, port, led_count):
  """Runs a changing color rainbow until interrupted."""
  strip = LPD8806(host, port, led_count)
  while True:
    RainbowCycle(strip)


def main():
  """Processes commandline input to setup the API server."""
  import optparse
  parser = optparse.OptionParser()
  parser.add_option('--host', default='192.168.178.16',
                    help='IP of the LPD8806-Ethernet device.')
  parser.add_option('-p', '--port', type='int', default=80,
                    help='Port of the LPD8806-Ethernet device.')
  parser.add_option('-l', '--leds', type='int', default=160,
                    help='Number of leds to drive.')
  options, _arguments = parser.parse_args()
  ForeverRainbows(options.host, options.port, options.leds)


if __name__ == '__main__':
  main()
