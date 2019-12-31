from datetime import date, timedelta
from notify import NotificationGenerator, Notification
from time import mktime

class WeekdayNotifier(NotificationGenerator):
  """
  Display a notification on specific days of the week

  - dow(int:0-6)
      The day of the week on which to display the message.  See:
      https://docs.python.org/3.5/library/datetime.html#datetime.date.weekday
      0 is Monday, 6 is Sunday.  
  - message(str)
      The message to display
  - icon(str)
      The icon to associate with the message
  - priority(int, optional)
      The priority at which to display the message
  - status("info"|"warning"|"danger", optional)
      The urgency of the message
  """

  def __init__(self, **kwargs):
    super(WeekdayNotifier, self).__init__()
    self.dow = kwargs["day_of_week"]
    self.message = kwargs["message"]
    self.icon = kwargs["icon"]
    self.priority = kwargs.get("priority", 0)
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
