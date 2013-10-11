#!/usr/bin/python2.7
"""Combine multiple ledstrips into one"""
import colors.py

class CombinedStrip(object):
  """Combines multiply ledstrips into one long string, allowing the user to send
  effects to all strips as if it where one long string"""

  def __init__(self, strips):
    """Sets up the combined strip

    Takes:
      strips: list of tuples(host,ip,led_count)
    """
    for strip in self.strips:
      self._strips.push(LPD8806(strip.host, strip.port, strip.led_count))

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
