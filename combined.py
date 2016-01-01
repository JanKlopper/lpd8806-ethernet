#!/usr/bin/python2.7
"""Combine multiple ledstrips into one"""
#custom imports
import colors

class CombinedStrip(object):
  """Combines multiply ledstrips into one long string, allowing the user to send
  effects to all strips as if it where one long string"""

  def __init__(self, strips):
    """Sets up the combined strip

    Takes:
      strips: list of tuples(host,ip,led_count)
    """
    self._strips = []
    self.led_count = 0
    for strip in strips:
      self.led_count = self.led_count + strip['led_count']
      self._strips.append(colors.LPD8806(strip['host'],
                                         strip['port'],
                                         strip['led_count'],
                                         strip['byte_order']))

  def getPixelColor(self, led):
    for strip in self._strips:
      try:
        return strip.getPixelColor(led)
      except KeyError:
        led = led - strip.led_count

  def setPixelColor(self, led, red, green, blue):
    """Sets the red, green and blue levels for a particular pixel."""
    offset = 0
    for strip in self._strips:
      if strip.led_count + offset > led:
        break
      offset = offset + strip.led_count
    strip.setPixelColor(led - offset, red, green, blue)

  def show(self):
    """Write out to all strips"""
    for strip in self._strips:
      strip.show()

def main():
  """Processes commandline input to setup the API server."""
  import optparse
  parser = optparse.OptionParser()
  parser.add_option('--hosts', default='192.168.178.210:80:160',
                    help='''comma seperated list of IPs of the LPD8806-Ethernet
                    devices, ip:host:ledcount,ip:host:ledcount''')
  parser.add_option('-e', '--effect', default='colorwipe',
                    help='Effect to apply.')
  options, arguments = parser.parse_args()
  hosts = options.hosts.split(',')
  strips = []
  for host in hosts:
    host = host.split(':')
    strips.append({
        'host': host[0],
        'port': int(host[1]),
        'led_count': int(host[2])})

  combined = CombinedStrip(strips)
  try:
    effect = getattr(colors.effects, options.effect)
  except AttributeError:
    print '%s not found, available effects are:' % options.effect
    #for effect in effects:
    help(colors.effects)
  arguments = map(int, arguments)
  effect(combined, *arguments)

if __name__ == '__main__':
  main()
