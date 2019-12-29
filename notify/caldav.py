from lib.CalDav import CalDav
from lib.Time import format_timedelta, days_until_start
from notify import NotificationGenerator, Notification

class CalDavNotifier(NotificationGenerator):

  def __init__(self, **kwargs):
    super(CalDavNotifier, self).__init__(
      poll_interval = kwargs.get("poll_interval", 5*60)
    )
    self.calendar = CalDav(
      url = kwargs["url"],
      calendars = kwargs["calendars"],
      user = kwargs["user"],
      password = kwargs["password"],
      window = kwargs["window"]
    )
    self.icon = kwargs.get("icon", "office/calendar-1")

  def update(self, hass):
    self.notifications = [
      Notification(
        body = "{}: {}".format(
          format_timedelta(event["start"]),
          event["summary"]
        ),
        priority = -days_until_start(event["start"]),
        icon = self.icon,
      )
      for event in self.calendar.events()
    ]