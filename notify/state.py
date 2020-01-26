from notify import NotificationGenerator, Notification
import iso8601
from datetime import datetime, timezone

class StateNotifier(NotificationGenerator):
  """
  A simple entity trigger-based notification generator.
  
  - entities(list of str)
      A list of entities to monitor
  - trigger(function: lib.HassLite.Hass -> bool)
      A condition to trigger a status update on
  - message(function: lib.HassLite.Hass -> str)
      The message to display in the notification
  - icon(str)
      The icon to associate with the notification
  - status("info"|"warning"|"danger", optional)
      The status to associate with the notification
  - priority(int, optional)
      The priority of the notification

  Whenever trigger() returns true, StateNotifier will generate one
  notification by calling message() to return a notification body.
  
  trigger() and message() will only be checked as a reaction to one of the
  listed entities being updated.
  """

  def __init__(self, entities, trigger, message, icon, status = "warning", priority = 1):
    super(StateNotifier, self).__init__(
      entity_triggers = entities
    )
    self.trigger = trigger
    self.message = message
    self.icon = icon
    self.status = status
    self.priority = priority

  def update(self, hass):
    self.notifications = [
      Notification(
        body = self.message(hass),
        status = self.status,
        icon = self.icon,
        priority = self.priority
      )
    ] if self.trigger(hass) else []


class SensorOfflineNotifier(NotificationGenerator):
  """
  A notification generator to detect sensors going offline.
  
  - entities(list of (str,str))
      A list of pairs of (human-readable name, hass entity) to monitor
  - timeout(int, optional)
      The amount of time (in seconds) since the sensor was last seen 
      before a notification gets triggered.  
  - icon(str, optional)
      The icon to associate with the notification
  - status("info"|"warning"|"danger", optional)
      The urgency of the resulting notification
  - priority(int, optional)
      The sort order priority of the resulting notification
  """

  def __init__(self, **kwargs):
    super(SensorOfflineNotifier, self).__init__(
      poll_interval = kwargs.get("poll_interval", 60*60),
      entity_triggers = [ entity for name, entity in kwargs.get("entities") ]
    )
    self.entities = kwargs.get("entities")
    self.icon = kwargs.get("icon", "devices/modem-1")
    self.status = kwargs.get("status", "danger")
    self.priority = kwargs.get("priority", 1)
    self.timeout = kwargs.get("timeout", 5*60*60)

  def last_update_timed_out(self, entity):
    if entity.last_updated == None:
      return False
    last_update = iso8601.parse_date(
      entity.last_updated,
      "%Y-%m-%dT%H:%M:%S.%f%z"
    )
    now = datetime.now(timezone.utc)
    delta = (now - last_update).seconds
    return delta > self.timeout

  def update(self, hass):
    self.notifications = [
      Notification(
        body = "{} offline".format(name),
        priority = self.priority,
        icon = self.icon,
        status = self.status
      )      
      for name, entity in self.entities
      if self.last_update_timed_out(hass[entity])
    ]

