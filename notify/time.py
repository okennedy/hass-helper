from datetime import date, timedelta
from notify import NotificationGenerator, Notification
from time import mktime

class WeekdayNotifier(NotificationGenerator):
  
  def __init__(self, **kwargs):
    super(WeekdayNotifier, self).__init__()
    self.dow = kwargs["day_of_week"]
    self.message = kwargs["message"]
    self.icon = kwargs["icon"]
    self.priority = kwargs.get("prioirty", 0)
    self.status = kwargs.get("status", "info")

  def update_poll_trigger(self):
    today = date.today()
    if today.weekday() == self.dow:
      tomorrow = today + timedelta(days = 1, hours = 1)
      self.next_poll_trigger = mktime(tomorrow.timetuple())
    else:
      days_until_next = (self.dow - today.weekday())%7
      trigger_date = today + timedelta(days = days_until_next, hours = 1)
      self.next_poll_trigger = mktime(trigger_date.timetuple())

  def update(self, hass):
    self.notifications = [
      Notification(
        body = self.message,
        priority = self.priority,
        status = self.status,
        icon = self.icon
      )
    ] if date.today().weekday() == self.dow else []
