#!/usr/bin/python
import telnetlib
import time
import random
"""ledstrip trough telnet-interface"""

numleds = 160;

def main():
  while True:
    rainbowCycle()
  #while True:
  #  colors = [(127,0,0), (0,140,0), (0,0,130), (50, 50, 0), (0, 40,90), (90, 10, 30)]
  #  Disco(colors, 10, 1)

  #colorChase(12,60,34)
  #colorChase(0,127,0)
  #colorChase(0,0,127)

# Slightly different, this one makes the rainbow wheel equally distributed
# along the chain
def rainbowCycle():
  strip = LPD8806(numleds)
  for j in xrange(0, 383*5): #5 cycles of all 384 colors in the wheel
    for i in xrange(0, strip.numPixels):
      # tricky math! we use each pixel as a fraction of the full 384-color wheel
      # (thats the i / strip.numPixels() part)
      # Then add in j which makes the colors go around per pixel
      # the % 384 is to make the wheel cycle around
      colors = Wheel( ((i * 384 / strip.numPixels) + j) % 384)
      strip.setPixelColor(i, colors[0], colors[1], colors[2])
    strip.show() # write all the pixels out

def Disco(colors, segments, delay):
  strip = LPD8806(numleds)
  segmentlength = strip.numPixels / segments

  for i in xrange(0, strip.numPixels):
    if i % segmentlength == 0:
      color = random.choice(colors)
    strip.setPixelColor(i, color[0], color[1], color[2])
  strip.show()
  time.sleep(delay)


def colorWipe(r,g,b):
  strip = LPD8806(numleds)
  for i in xrange(0, strip.numPixels):
    strip.setPixelColor(i, r, g, b)
    strip.show()
    time.sleep(.2)

def colorChase(r, g, b):
  strip = LPD8806(numleds)
  # Chase one dot down the full strip.

  # Start by turning all pixels off:
  for i in xrange(0, strip.numPixels):
    strip.setPixelColor(i, 0, 0, 0);

  # Then display one pixel at a time:
  for i in xrange(0, strip.numPixels):
    strip.setPixelColor(i, r,g,b) # Set new pixel 'on'
    strip.show()                  # Refresh LED states
    strip.setPixelColor(i, 0,0,0) # Erase pixel, but don't refresh!
    time.sleep(.2)
  strip.show() # Refresh to turn off last pixel


def rainbow():
  strip = LPD8806(numleds)
  for j in xrange(0, 383): # 3 cycles of all 384 colors in the wheel
    for i in xrange(0, strip.numPixels):
      colors = Wheel( (i + j) % 384)
      strip.setPixelColor(i, colors[0], colors[1], colors[2])
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
  return (r,g,b);

class LPD8806(object):

  def __init__(self, numleds):
    self.leds = {}
    self.numPixels = numleds;

  def setPixelColor(self, led, r, g, b):
    self.leds[led] = (r, g, b)

  def show(self):

    output = []
    try:
      for led in xrange(0, self.numPixels):
        output.append(chr(self.leds[led][0]+65))
        output.append(chr(self.leds[led][1]+65))
        output.append(chr(self.leds[led][2]+65))
        print chr(self.leds[led][0]+65) + chr(self.leds[led][1]+65) + chr(self.leds[led][2]+65)
    except KeyError:
      output.append('AAA')

    t = telnetlib.Telnet('192.168.178.16', 80)
    t.write(''.join(output))
    t.close()

if __name__ == '__main__':
  main()
