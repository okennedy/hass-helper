import json
from lib.HassLite import Hass
from notify import NotificationManager
from time import sleep
from time import time as get_now

class HassHelper:
  def __init__(self, host, api_key, noitfication_entity = "status.housewide"):
    self.hass = Hass(host, api_key)
    self.notifications = NotificationManager(self, noitfication_entity)
    self.hass.start_thread()
    self.managers = [
      self.notifications
    ]

  def refresh(self):
    for manager in self.managers:
      manager.update()

  def run(self):
    self.refresh()
    self.poll_loop()

  def poll_loop(self):
    while True:
      now = get_now()
      next_trigger = min([
          manager.next_poll_trigger
          for manager in self.managers 
          if manager.next_poll_trigger is not None
        ], default = now + 600
      )
      sleep_time = next_trigger - now
      # print("Next Trigger in {} seconds".format(sleep_time))
      if sleep_time > 0:
        sleep(sleep_time)
      for manager in self.managers:
        # print("Checking: {}".format(manager))
        if manager.next_poll_trigger < now+1:
          manager.update()

