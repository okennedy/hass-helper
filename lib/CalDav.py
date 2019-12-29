
from time import time as now
from datetime import date, datetime, timedelta
import requests
import caldav
from caldav.elements import dav, cdav
from tzlocal import get_localzone
import feedparser

def extract_events_from_event_set(event_set):
  if hasattr(event_set.instance, 'vcalendar'):
      return event_set.instance.components()
  elif hasattr(event_set.instance, 'vevent'):
      return [ event_set.instance.vevent ]

def extract_summary_from_event(event):
  for summary_attr in ('summary', 'location', 'description'):
    if hasattr(event, summary_attr):
      return getattr(event, summary_attr).value
    return "No Description"

def caldav_time_to_struct(t):
  if isinstance(t.value, datetime):
    t = t.value.astimezone(get_localzone())
    return {
      "allday": False,
      "year":   int(t.year), 
      "month":  int(t.month), 
      "day":    int(t.day),
      "hour":   int(t.hour),
      "minute": int(t.minute)
    }
  elif isinstance(t.value, date):
    return {
      "allday": True,
      "year":   t.value.year, 
      "month":  t.value.month, 
      "day":    t.value.day
    }
  else:
    raise Exception("Unknown type of {}".format(t.value)) 

class CalDav:
  def __init__(self, **kwargs):
    self.window       = kwargs.get("window", 60*60*24*7)
    self.client       = caldav.DAVClient(
      kwargs["url"],
      username = kwargs["user"],
      password = kwargs["password"]
    )
    self.principal = self.client.principal()
    self.all_calendars = dict([
      (calendar.get_properties([dav.DisplayName()])["{DAV:}displayname"], calendar)
      for calendar in self.principal.calendars()
    ])
    #print(self.all_calendars)
    self.calendars = [ 
      self.all_calendars[name] 
      for name in kwargs["calendars"] 
    ]

  def events(self):
    return [
      {
        "start" :   caldav_time_to_struct(event.dtstart),
        "end" :     caldav_time_to_struct(event.dtend),
        "summary" : extract_summary_from_event(event)
      }
      for calendar in self.calendars
      for event_set in calendar.date_search(
            datetime.now(),
            datetime.now() + timedelta(seconds = self.window)
          )
      for event in extract_events_from_event_set(event_set)
    ]

