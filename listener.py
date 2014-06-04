#!/usr/bin/python2.7
"""This listener takes commands from the backend and makes sure the combined 
strip is being updated."""
__author__ = 'Jan KLopper (janklopper@innerheight.com)'
__version__ = 0.1

import combined 
import MySQLdb
import simplejson
import time

class CancelEffect(Exception):
  pass

class ServerStrip(combined.CombinedStrip):
  """Server based strip management"""   
  def __init__(self, options, strips):
    super(ServerStrip, self).__init__(strips)
    self.effect = {'ID': 0 }
    self.connection = MySQLdb.connect(
        host=options.mysql,
        user=options.mysqluser,
        passwd=options.mysqlpassword,
        db=options.mysqldatabase)
    self.minsleep = 0.01
    self.sleep = 0.1
    self.maxsleep = 2

  def Run(self):
    currentEffect = self.FetchMessage()
    if currentEffect:
      self.effect = currentEffect
      try:
        effect = getattr(combined.colors.effects, self.effect['effect'])
      except AttributeError:
        print 'unknown effect: %s' % self.effect['effect']
        return
      self.sleep = self.minsleep
      if self.effect['arguments']:     
        effect(self, *self.effect['arguments'])
      else:
        effect(self)
    else:
      time.sleep(self.sleep) 
      self.sleep = min(self.sleep * 2, self.maxsleep)

  def FetchMessage(self, checkCancel=False):
    cursor = self.connection.cursor()
    conditions = ''
    if checkCancel:
      conditions = 'and cancelprevious = 1'

    cursor.execute("SELECT * FROM `effects` where id>%d %s" % (
        self.effect['ID'], conditions))
    self.connection.commit()
    row = cursor.fetchone()
    if row:
      return {'ID': int(row[0]),
              'effect': row[1],
              'arguments': self.ParseArguments(row[2]),
              'dateCreated': row[3],
              'cancelPrevious': bool(int(row[4]))}
    else:
      return False
               
  def ParseArguments(self, inputString):
    if inputString	 and inputString != '':
      row = simplejson.loads(inputString)
      newrow = []
      for column in row:
        try:
          if ',' in column:
            column = float(column)
          else:
            column = int(column)
        except:
          pass
        newrow.append(column)
      return newrow
    return None

  def show(self):
    """Write out to all strips"""
    effect = self.FetchMessage(True)
    if effect and effect['cancelPrevious']:
      print 'canceling previous effect'
      self.currentEffect = effect
      raise CancelEffect
    #print 'effect ID %d' % self.effect['ID']
    
    for strip in self._strips:
      #print 'output on strip %s' % strip.host
      strip.show()

def main():
  """Processes commandline input to setup the API server."""
  import optparse
  parser = optparse.OptionParser()
  parser.add_option('--hosts', default='192.168.178.210:80:160',
                    help='''comma seperated list of IPs of the LPD8806-Ethernet
                    devices, ip:host:ledcount,ip:host:ledcount''')
  parser.add_option('-m', '--mysql', default='localhost',
                    help='Mysql server to connect to')
  parser.add_option('-d', '--mysqldatabase', default='lightstrips',
                    help='Mysql database to use')
  parser.add_option('-u', '--mysqluser', help='Mysql username')
  parser.add_option('-p', '--mysqlpassword', help='Mysql password')
  options, arguments = parser.parse_args()
  hosts = options.hosts.split(',')
  strips = []
  for host in hosts:
    host = host.split(':')
    strips.append({
        'host': host[0],
        'port': int(host[1]),
        'led_count': int(host[2])})

  serverstrip = ServerStrip(options, strips)
  while True:
    try:
      serverstrip.Run()
    except CancelEffect:
      pass 

if __name__ == '__main__':
  main() 
