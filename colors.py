#!/usr/bin/python2.7
"""ledstrip trough telnet-interface"""
import telnetlib

#custom imports
import effects

class LPD8806(object):
  """LPD8806 RGB strip abstraction."""
  def __init__(self, host, port, led_count):
    self.host = host
    self.port = port
    self.led_count = led_count
    self.leds = {}

  def setPixelColor(self, led, red, green, blue):
    """Sets the red, green and blue levels for a particular pixel."""
    self.leds[led] = green, red, blue

  def show(self):
    """Writes out all pixels to the ethernet listener."""
    output = []
    for led in range(self.led_count):
      try:
        for channel in self.leds[led]:
          output.append(chr(channel + 65))
        #print ''.join(output[-3:])
      except KeyError:
        # No color is defined, set the pixel to black
        output.append('AAA')
    tn = telnetlib.Telnet(self.host, self.port)
    tn.write(''.join(output))

def main():
  """Processes commandline input to setup the API server."""
  import optparse
  parser = optparse.OptionParser()
  parser.add_option('--host', default='192.168.178.210',
                    help='IP of the LPD8806-Ethernet device.')
  parser.add_option('-p', '--port', type='int', default=80,
                    help='Port of the LPD8806-Ethernet device.')
  parser.add_option('-l', '--leds', type='int', default=160,
                    help='Number of leds to drive.')
  parser.add_option('-e', '--effect', default='colorwipe',
                    help='Effect to apply.')
  options, arguments = parser.parse_args()
  strip = LPD8806(options.host, options.port, options.leds)
  try:
    effect = getattr(effects, options.effect)
  except AttributeError:
    print '%s not found, available effects are:' % options.effect
    #for effect in effects:
    help(effects)
  arguments = map(int, arguments)
  effect(strip, *arguments)

if __name__ == '__main__':
  main()
