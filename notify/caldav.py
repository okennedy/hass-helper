from lib.CalDav import CalDav
from lib.Time import format_timedelta, days_until_start
from lib.Unicode import extract_emoji
from notify import NotificationGenerator, Notification

class CalDavNotifier(NotificationGenerator):
  """
  Generate notifications for events from a CalDav server

  - url(str)               : The URL of the caldav server+path
  - calendars(list of str) : A list of calendars to display
  - user(str)              : The CalDav username
  - password(str)          : The CalDav password
  - window(int)            : How far into the future (in seconds) 
                             to display notifications
  """

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
          text
        ),
        priority = -days_until_start(event["start"]),
        icon = "calendar-emoji/{:x}".format(ord(icon[0])) if len(icon) > 0 else self.icon,
      )
      for event in self.calendar.events()
      for icon, text in [extract_emoji(event["summary"])]
    ]