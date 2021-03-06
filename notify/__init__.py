import requests
import json  
from time import time as get_now

def Notification(**kvargs):
  """
  Generate a notification object.

  - body(str, optional) 
      The text of the notification
  - status("info"|"warning"|"danger", optional)
      The urgency level of the notification
  - priority(int, optional)
      The priority (how high in the list) of the notification
  - action(str, optional)
      Unused, eventually meant to enable on-click callbacks
  - icon(str, optional)
      The icon to associate with the notification
  """
  return { 
    "body" : kvargs.get("body", "Unknown Notification"),
    "status" : kvargs.get("status", "info"),
    "priority" : kvargs.get("priority", 0),
    "action" : kvargs.get("action", ""),
    "icon" : kvargs.get("icon", "office/artboard")
  }

class NotificationGenerator:
  """
  Abstract superclass of notification generators.  See individual files in
  this package for examples.  To implement a new generator, override
  `update` and provide one or more of the following to the constructor:
    - poll_interval(int, optional):
        This will trigger update() every `poll_interval` seconds.
    - Pass entity_triggers(list of str, optional):
        This will trigger update() every time one of the listed entities
        updates its state
  Additionally, you may override update_poll_trigger to specify a variable
  polling interval.  See `notify.time.WeekdayNotifier` for an example.
  """
  def __init__(self, poll_interval = None, entity_triggers = []):
    self.poll_interval = poll_interval
    self.entity_triggers = entity_triggers
    if self.poll_interval is not None:
      self.next_poll_trigger = get_now()
    else:
      self.next_poll_trigger = None
    self.notifications = []
    # print(self.next_poll_trigger)

  def update_poll_trigger(self):
    """
    Figure out the unix timestamp at which the next polling update() should
    trigger.  Override this function to set a dynamic trigger.
    """
    if self.poll_interval is not None:
      self.next_poll_trigger = get_now() + self.poll_interval

  def update(self, hass):
    """
    Update this generator's notifications.  This function should be overridden
    by any subclass.  The overriding function should set self.notifications
    to a list of objects returned by calling `notify.Notification(...)`
    """
    self.notifications = [
      Notification(
        body = "No notifications generated for {}".format(self)
      )
    ]

class NotificationManager:
  """
  Manager class for `NotificationGenerator`s.  Generally this gets
  instantiated by HassHelper and is accessed as `helper.notifications`

  - helper(str) : The HassHelper instance to associate with 
  - entity(str) : The sensor entity to register notifications under.
  """

  def __init__(self, helper, entity):
    self.helper = helper
    self.entity = entity
    self.generators = []
    self.next_poll_trigger = None

  def add(self, generator):
    """
    Register a new `NotificationGenerator`

    - generator(NotificationGenerator): The generator subclass/instance to register
    """
    self.generators += [generator]
    generator.update(self.helper.hass)
    generator.update_poll_trigger()
    if self.next_poll_trigger is None:
      self.next_poll_trigger = generator.next_poll_trigger
    elif generator.next_poll_trigger is not None:
      self.next_poll_trigger = min(generator.next_poll_trigger, self.next_poll_trigger)
    for entity in generator.entity_triggers:
      self.helper.hass.add_callback(
        lambda state, attributes: self.call_trigger(generator),
        entity
      )

  def call_trigger(self, generator):
    """
    Internal: Used to react to an update event. Invokes the generator's update() method
    and updates the notification entity.

    - generator(NotificationGenerator): The generator to update()
    """
    generator.update(self.helper.hass)
    self.post()

  def update(self):
    """
    Force an update of all generators who's poll trigger has expired and ask each 
    expired generator to compute its next poll trigger.
    """
    print("Update Notifications!")
    now = get_now()
    for gen in self.generators:
      if gen.next_poll_trigger is not None and gen.next_poll_trigger < now:
        gen.update(self.helper.hass)
        gen.update_poll_trigger()
    self.next_poll_trigger = min([
        gen.next_poll_trigger
        for gen in self.generators
        if gen.next_poll_trigger is not None
      ], default = None
    )
    self.post()

  def post(self):
    """
    Post the notification list to home assistant
    """
    notifications = [
      notification
      for gen in self.generators
      for notification in gen.notifications
    ]
    notifications.sort(key = lambda x: -x["priority"])
    if len(notifications) < 1:
      notifications = [
        Notification(
          body = "Nothing to report"
        )
      ]
    print("Current Notifications: {}".format(notifications))
    ret = self.helper.hass.post_update(
      self.entity, 
      state = len(notifications),
      attributes = {
        "notifications" : notifications,
        "unit_of_measurement" : "Notifications"
      }
    )
    print(ret.text)
