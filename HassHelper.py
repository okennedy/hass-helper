import json
from lib.HassLite import Hass
from notify import NotificationManager
from time import sleep
from time import time as get_now

class HassHelper:
  """
  Server class for home assistant helper.

  - host(str)                : The root URL of the home assistant server
  - api_key(str)             : The API KEY home assistant was configured with
  - notification_entity(str) : The name of the sensor entity to create

  Once a HassHelper instance (`helper`) has been created, use `helper.run()` 
  to start the server.

  In addition to triggering timed events through the poll_loop below, 
  callbacks may also be registered through `helper.hass` (see lib.HassLite).
  """

  def __init__(self, host, api_key, notification_entity = "status.housewide"):
    self.hass = Hass(host, api_key)
    self.notifications = NotificationManager(self, notification_entity)
    self.hass.start_thread()
    self.managers = [
      self.notifications
    ]

  def refresh(self):
    """
    Refresh all of the sensor managers
    """
    for manager in self.managers:
      manager.update()

  def run(self):
    """
    Normal way to start the server
    """
    self.refresh()
    self.poll_loop()

  def poll_loop(self):
    """
    Internal only: Infinite loop that monitors updates
    """
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

