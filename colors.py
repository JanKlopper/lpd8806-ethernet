#!/usr/bin/python
"""ledstrip trough telnet-interface"""
import telnetlib
import time
import random


class LPD8806(object):
  """LPD8806 RGB strip abstraction."""
  def __init__(self, host, port, led_count):
    self.host = host
    self.port = port
    self.led_count = led_count
    self.leds = {}

  def setPixelColor(self, led, red, green, blue):
    """Sets the red, green and blue levels for a particular pixel."""
    self.leds[led] = red, green, blue

  def show(self):
    """Writes out all pixels to the ethernet listener."""
    output = []
    for led in range(self.led_count):
      try:
        for channel in self.leds[led]:
          output.append(chr(channel + 65))
        print ''.join(output[-3:])
      except KeyError:
        # No color is defined, set the pixel to black
        output.append('AAA')
    with telnetlib.Telnet(self.host, self.port) as tn:
      tn.write(''.join(output))


def colorChase(strip, r, g, b, delay=0.2):
  """Chase one dot down the full strip."""
  # Start by turning all pixels off:
  for led in range(strip.led_count):
    strip.setPixelColor(led, 0, 0, 0)

  # Then display one pixel at a time:
  for led in range(strip.led_count):
    strip.setPixelColor(led, r, g, b) # Set new pixel 'on'
    strip.show()                      # Refresh LED states
    strip.setPixelColor(led, 0, 0, 0) # Erase pixel, but don't refresh!
    time.sleep(delay)
  strip.show() # Refresh to turn off last pixel


def colorWipe(strip, r, g, b, delay=0.2):
  """Fills the strip from begin to end with a single color."""
  for led in range(strip.led_count):
    strip.setPixelColor(led, r, g, b)
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


def foreverRainbow(host, port, led_count):
  """Runs a changing color rainbow until interrupted."""
  strip = LPD8806(host, port, led_count)
  while True:
    rainbowCycle(strip)


def rainbow(strip):
  """Cycles all LED's on the strip through the full color wheel."""
  for angle in range(384):
    for led in range(strip.led_count):
      color = wheel((led + angle) % 384)
      strip.setPixelColor(led, *color)
    strip.show()


def rainbowCycle(strip, repeats=5):
  """Perform a quick rainbow cycle."""
  for _repeat in range(repeats):
    for angle in range(384):
      for led in range(strip.led_count):
        # We use each pixel as a fraction of the full 384-color wheel
        # (thats the led / strip.led_count() part)
        # Then add in the angle which makes the colors go around per pixel
        # the % 384 is to make the wheel cycle around
        colors = wheel( ((led * 384 / strip.led_count) + angle) % 384)
        strip.setPixelColor(led, *colors)
      strip.show() # write all the pixels out


def wheel(angle):
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
  foreverRainbow(options.host, options.port, options.leds)


if __name__ == '__main__':
  main()
