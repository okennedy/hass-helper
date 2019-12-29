import requests
import json  
from time import time as get_now

def Notification(**kvargs):
  return { 
    "body" : kvargs.get("body", "Unknown Notification"),
    "status" : kvargs.get("status", "info"),
    "priority" : kvargs.get("priority", 0),
    "action" : kvargs.get("action", ""),
    "icon" : kvargs.get("icon", "office/artboard")
  }

class NotificationGenerator:
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
    if self.poll_interval is not None:
      self.next_poll_trigger = get_now() + self.poll_interval

  def update(self, hass):
    self.notifications = [
      Notification(
        body = "No notifications generated for {}".format(self)
      )
    ]

class NotificationManager:
  def __init__(self, helper, entity):
    self.helper = helper
    self.entity = entity
    self.generators = []
    self.next_poll_trigger = None

  def add(self, generator):
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
    generator.update(self.helper.hass)
    self.post()

  def update(self):
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
