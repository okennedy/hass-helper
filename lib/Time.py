from datetime import date, datetime

def to_date(time):
  return date(time["year"], time["month"], time["day"])

def to_datetime(time):
  if(time["allday"]):
    return datetime(time["year"], time["month"], time["day"])
  else:
    return datetime(time["year"], time["month"], time["day"], time["hour"], time["minute"])

def is_over(time):
  if(time["allday"]):
    date.today() > to_date(time)
  else:
    datetime.now() > to_datetime(time)

def days_until_start(time):
  return (to_date(time) - date.today()).days

def format_hour(time):
  h = time.hour
  m = time.minute
  am_pm = "AM"
  if (m == 0) and (h == 12):
    return "Noon"
  elif (m == 0) and (h == 0):
    return "Midnight"
  elif h > 12:
    h -= 12
    am_pm = "PM"

  if(m > 0):
    m = ":{}".format(m)
  else:
    m = ""
  return "{}{} {}".format(h, m, am_pm)

def format_timedelta(time):
  if time["allday"]:
    event = to_date(time)
    days = (event - date.today()).days
    if(days < 0): 
      return "Now" #{} days ago".format(days)
    elif(days == 0):
      return "Today"
    elif(days == 1):
      return "Tomorrow"
    elif(days < 5):
      return "{}".format(event.strftime("%A"))
    elif(days < 9):
      return "Next {}".format(event.strftime("%A"))
    else:
      return "In {} weeks".format(int(days / 7))
  else:
    event = to_datetime(time)
    delta = (event - datetime.now())
    days = (to_date(time) - date.today()).days
    if days > 0:
      if(days < 0): 
        return "{} days ago".format(days)
      elif(days == 0):
        return "Today at {}".format(format_hour(event))
      elif(days == 1):
        return "Tomorrow at {}".format(format_hour(event))
      elif(days < 5):
        return "{} at {}".format(event.strftime("%A"), format_hour(event))
      elif(days < 9):
        return "Next {} at {}".format(event.strftime("%A"), format_hour(event))
      else:
        return "In {} weeks".format(int(days / 7))
    else:
      seconds = delta.seconds
      if(seconds < 360): # Signal start ~10 minutes away
        return "Now"
      elif(seconds < 90*60): # Start showing minutes 90 minutes away
        return "In {} minutes".format(int(seconds / 60))
      elif(seconds < 3*3600): # Start showing hours 3 hours away
        return "In {} hours".format(int(seconds / 3600))
      else:
        return "Today at {}".format(format_hour(event))
