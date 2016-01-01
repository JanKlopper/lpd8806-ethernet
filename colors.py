#!/usr/bin/python2.7
"""ledstrip trough telnet-interface"""
import telnetlib
import socket

#custom imports
import effects

class LPD8806(object):
  """LPD8806 RGB strip abstraction."""
  def __init__(self, host, port=80, led_count=160, byte_order='rgb'):
    self.host = host
    self.port = port
    self.led_count = led_count
    self.byte_order = byte_order
    self.leds = {}
    self.version = 1
    self.magic = 'LP'
    self.active = True

  def getPixelColor(self, led):
    if led > self.led_count:
      raise KeyError
    return self.leds[led]

  def setPixelColor(self, led, red, green, blue):
    """Sets the red, green and blue levels for a particular pixel."""
    if self.byte_order == 'grb':
      self.leds[led] = green, red, blue
    elif self.byte_order == 'rgb':
      self.leds[led] = red, green, blue
    elif self.byte_order == 'brg':
      self.leds[led] = blue, red, green
    elif self.byte_order == 'rbg':
      self.leds[led] = red, blue, green

  def show(self):
    """Writes out all pixels to the ethernet listener."""
    if not self.active:
	return
    output = []
    output.append(self.magic)
    output.append(str(self.version))

    for led in range(self.led_count):
      try:
        for channel in self.leds[led]:
          output.append(chr(channel + 65))
        #print ''.join(output[-3:])
      except KeyError:
        # No color is defined, set the pixel to black
        output.append('AAA')
      except ValueError:
        print 'trying to output %d for led %d' % (channel, led)
    try:
      tn = telnetlib.Telnet(self.host, self.port)
      tn.write(''.join(output))
    except socket.error, error:
      print '%s for %s, removing from pool' % (error, self.host)
      self.active = False
      pass

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
