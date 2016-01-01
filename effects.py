#!/usr/bin/python2.7
"""Various effects available for the lpd8806 ledstrip"""

# Standard imports
import time
import random
import math

def colorChase(strip, red, green, blue, delay=0.2):
  """Chase one dot down the full strip."""
  # Start by turning all pixels off:
  for led in range(strip.led_count):
    strip.setPixelColor(led, 0, 0, 0)

  # Then display one pixel at a time:
  for led in range(strip.led_count):
    strip.setPixelColor(led, red, green, blue) # Set new pixel 'on'
    strip.show()                      # Refresh LED states
    strip.setPixelColor(led, 0, 0, 0) # Erase pixel, but don't refresh!
    time.sleep(delay)
  strip.show() # Refresh to turn off last pixel

def colorWipe(strip, red, green, blue, delay=0.2):
  """Fills the strip from begin to end with a single color."""
  for led in range(strip.led_count):
    strip.setPixelColor(led,red, green, blue)
    strip.show()
    time.sleep(delay)

def pilars(strip, red, green, blue):
  """Fills the strip at the pilar possitions with a single color."""
  off(strip)
  for led in range(51, 61):
    strip.setPixelColor(led,red, green, blue)
  for led in range(164, 175):
    strip.setPixelColor(led,red, green, blue)
  for led in range(216, 227):
    strip.setPixelColor(led,red, green, blue)
  strip.show()

def plants(strip, red, green, blue):
  """Fills the strip at the plant positions with a single color."""
  off(strip)
  for led in range(164, 175):
    strip.setPixelColor(led,red, green, blue)
  for led in range(216, 227):
    strip.setPixelColor(led,red, green, blue)
  strip.show()

def twinkle(strip, red, green, blue, amount, delay=0.05):
  off(strip)
  prevamount = 0
  levels = (0,0,2,2,2,2,4,8)
  while True:
    # gradually ease in enough leds
    randoms = random.sample(xrange(strip.led_count),
                            int(((amount+1) - prevamount) / 2))
    # pick the start color and make it even
    startred = 5
    startgreen = 5
    startblue = 5
    prevamount = 0

    for led in range(strip.led_count):
      # add a new led
      if led in randoms:
        prevamount = prevamount + 1
        strip.setPixelColor(led, startred, startgreen, startblue)

      # check all leds to see if they are lit up, and either go up, or down
      currentlevel = strip.getPixelColor(led)
      if currentlevel:
        #print led, currentlevel
        change = random.choice(levels)

        # if the currentlevel is odd, we need to increase the intensity,
        # untill we hit the max
        if currentlevel[0] % 2:
          prevamount = prevamount + 1
          if (currentlevel[0]+change) <= red:
           # print 'up for %d = %d' % (led, currentlevel[0])
            strip.setPixelColor(led,
                min(currentlevel[0]+change, 255),
                min(currentlevel[1]+change, 255),
                min(currentlevel[2]+change, 255))
          else:
            #print 'inverse for %d = %d' % (led, currentlevel[0])
            strip.setPixelColor(led,
                currentlevel[0]+1,
                currentlevel[1]+1,
                currentlevel[2]+1)
        elif currentlevel[0] > 0:
          # else decrease the color to 0
          if currentlevel[0]-4 >= 0:
            prevamount = prevamount + 1
            #print 'down for %d = %d' % (led, currentlevel[0])
            strip.setPixelColor(led,
                max(0, currentlevel[0]-change),
                max(0, currentlevel[1]-change),
                max(0, currentlevel[2]-change))
          else:
            #print 'off for %d = %d' % (led, currentlevel[0])
            strip.setPixelColor(led, 0 ,0 ,0)
    strip.show()
    time.sleep(delay)

def disco(strip, colors, segments, delay):
  """Place random colors on segments of the LED-strip."""
  segmentlength = strip.led_count / segments
  for led in range(strip.led_count):
    if not led % segmentlength:
      color = random.choice(colors)
    strip.setPixelColor(led, *color)
  strip.show()
  time.sleep(delay)

def rainbow(strip):
  """Cycles all LED's on the strip through the full color wheel."""
  for angle in range(384):
    for led in range(strip.led_count):
      # We use each pixel as a fraction of the full 384-color wheel
      # (thats the led / strip.led_count() part)
      # Then add in the angle which makes the colors go around per pixel
      # the % 384 is to make the wheel cycle around    
      colors = wheel( ((led * 384 / strip.led_count) + angle) % 384)
      strip.setPixelColor(led, *colors)
    strip.show()

def rainbowCycle(strip, cycles=5):
  """Perform a quick rainbow cycle"""
  if cycles > 0:
    for _repeat in range(cycles):
      rainbow(strip)
  else:
    while True:
      rainbow(strip)

def solidcolor(strip, red, green, blue):
  for led in range(strip.led_count):
    strip.setPixelColor(led, red, green, blue)
  strip.show()

def off(strip):
  solidcolor(strip, 0, 0, 0)

def wheel(angle):
  """Helper function for the rainbows"""
  if angle / 128 == 0:
    r = 127 - angle % 128    # Red down
    g = angle % 128          # Green up
    b = 0                    # blue off
  elif angle / 128 == 1:
    g = 127 - angle % 128    # green down
    b = angle % 128          # blue up
    r = 0                    #red off
  elif angle / 128 == 2:
    b = 127 - angle % 128    # blue down
    r = angle % 128          # red up
    g = 0                    # green off
  return r, g, b
