import json
import requests
from os.path import expanduser

from lib.Time import format_timedelta, days_until_start
from lib.CalDav import CalDav
from datetime import date, datetime, timedelta, timezone
from time import time as get_now
from dateutil import parser as date_parser
import iso8601
from tasklib import TaskWarrior
import re

with open(expanduser("~/.hass-notifier")) as config:
  config = json.load(config)


def notifications_to_hass(notifications):
  state = "{} notification{}".format(len(notifications), "s" if len(notifications) != 1 else "")
  return json.dumps({
    "state" : state,
    "attributes" : {
      "notifications" : notifications
      # "count" : len(data)
      # **dict([
      #   (key+"_"+i, notification[key])
      #   for notification in notifications
      #   for key, i in zip(notification.keys(), range(0, len(notification.keys())))
      # ])
    }
  })

def post_notifications(notifications):
  global config
  url = "{}/api/states/status.housewide".format(config["host"])
  headers = {
    "x-ha-access" : config["api_key"],
    "Content-Type" : "application/json"
  }
  r = requests.post(url, data = notifications_to_hass(notifications), headers=headers)
  print(r.text)

def get_state(entity):
  global config
  url = "{}/api/states/{}".format(config["host"], entity)
  headers = {
    "x-ha-access" : config["api_key"],
    "Content-Type" : "application/json"
  }
  r = requests.get(url, headers=headers)
  return r.json()

def Notification(**kvargs):
  return { 
    "body" : kvargs.get("body", "Unknown Notification"),
    "status" : kvargs.get("status", "info"),
    "priority" : kvargs.get("priority", 0),
    "action" : kvargs.get("action", ""),
    "icon" : kvargs.get("icon", "office/artboard")
  }

notifications = []

#notifications += [
#  Notification(body = "Test 1")
#]
  
###################### Tasks ##########################
tw = TaskWarrior()
for task in tw.tasks.filter(status='pending', tags__contains=['home']):
  description = task['description']
  description = re.sub(" +\\(.+", "", description)
  days_until_due = (task['due'] - datetime.now(timezone.utc)).days
  if days_until_due < 10:
    notifications += [
      Notification(
        body = description,
        priority = -days_until_due,
        status = "warning" if days_until_due < 0 else "info",
        icon = "office/notes"
      )
  ]
#    
#  >>> tasks[0]['due']
#  datetime.datetime(2019, 11, 15, 0, 0, tzinfo=<DstTzInfo 'America/New_York' EST-1 day, 19:00:00 STD>)
#  >>> tasks[0]['description']
#  'Get Gutters Cleaned: Richard Young Window Cleaning Service ( http://RichardYoungWindowCleaning.com (716) 627-9324 )'
#  >>>
  

###################### Calendar Events ##########################
calendar = CalDav(
  url="https://cloud.okennedy.org/remote.php/dav",
  calendars=["Family (Oliver Kennedy)"],
  user="bot",
  password=config["caldav_key"],
  window=604800 # 1 week
)

notifications += [
  Notification(
    body = "{}: {}".format(
      format_timedelta(event["start"]),
      event["summary"]
    ),
    priority = -days_until_start(event["start"]),
    icon = "office/calendar-1",
  )
  for event in calendar.events()
]

###################### Trash Day ##########################
if datetime.today().weekday() == 3: # Show only on Thursday only
  notifications += [
    Notification(
      body = "Walk out the trash",
      priority = 0,
      icon = "ecology/recycling-1",
      status = "warning"
#      action = "http://serenity/data/chores/curb_trash?complete=yes" if (now - trash["last_performed"] > 345600) else None
    )
  ]
  
###################### Sump Well Sensors ##########################

## The analog liquid depth sensor is finicky.  Even slightly jostling the
## connectors can trigger a need for recalibration.  It'll stabilize at
## some point... figure out where it is, knock off 10-20%, and trigger
## the warning off of that point.  OR... if the digital sensor proves
## to be good enough, we can transition to relying on that one 100%
analog_sump_sensor = get_state("sensor.sump_liquid_level")
analog_trigger_level = 1600
digital_sump_sensor = get_state("binary_sensor.sump_well_overflow")
if float(analog_sump_sensor["state"]) < analog_trigger_level or digital_sump_sensor["state"] == "on":
  notifications += [
    Notification(
      body = "The sump pump might be down",
      status = "danger",
      icon = "ecology/water-tap",
      priority = 2
    )
  ]

###################### Garage Door ##########################
garage_door = get_state("sensor.garage_door")
if garage_door["state"] != "closed":
  notifications += [
    Notification(
      body = "The garage door is {}".format(garage_door["state"]),
      status = "warning",
      icon = "transportation/car",
      priority = 1
    )
  ]

###################### Offline Sensors ##########################
check_sensors = [
  ("Office", "sensor.office_temperature"),
  ("Armory", "sensor.armory_temperature"),
  ("Furnace", "sensor.furnace_humidity"), # Use humidity sensor... temperature down there is too stable!
  ("Sump Well Area", "sensor.sump_liquid_level"),
  ("Garage", "sensor.garage_temperature")
]

now = datetime.now(timezone.utc)
for (area, sensor) in check_sensors:
  state = get_state(sensor)
  error = False
  if "state" in state:
    last_update = iso8601.parse_date(
      state["last_updated"],
      "%Y-%m-%dT%H:%M:%S.%f%z"
    )
    delta = (now - last_update).seconds
    if(delta > 5*60*60): # 5 hours
      error = True
  else:
    error = True

  if error:
    notifications += [
      Notification(
        body = "{} area sensor offline".format(area),
        priority = 1,
        icon = "devices/modem-1",
        status = "danger"
      )
    ]


###################### Sort notifications ##########################
notifications.sort(key = lambda x: -x["priority"])

###################### Ensure at least one notification ##########################
if len(notifications) < 1:
  notifications = [
    Notification(
      body = "Nothing to report"
    )
  ]

###################### And post them ##########################
#print(notifications)
post_notifications(notifications)

 #        for event in try_lookup(status, ["sump_pump"])
 #        if "depth" in event and "resistance" in event["depth"] and event["depth"]["resistance"] < 1500
 #      ] + [
 #        Notification(
 #          body = "Sump pump sensor malfunction",
 #          status = "warning",
 #          icon = "ecology/water-tap",
 #          priority = 3
 #        )
 #        for event in try_lookup(status, ["sump_pump"])
 #        if "depth" not in event or "resistance" not in event["depth"]
 #      ] + [
 #        Notification(
 #          body = "{} until {}".format(
 #            event["description"], 
 #            event["expires"]
 #          ),
 #          priority = 1 if event["significance"] == "Y" else 0,
 #          icon = "weather/storm-1",
 #          status = "warning" if event["significance"] == "Y" else "info"
 #        )
 #        for event in try_lookup_list(self.root, ["weather", "alerts", "alerts"])
 #      ] + [
 #      ] + [
 #        Notification(
 #          body = "No updates from {} in {}".format(node, timedelta(seconds = now - lookup(status, [node, "last_update"]))),
 #          priority = 2,
 #          icon = "technology/transfer",
 #          status = "danger"
 #        )
 #        for node in [ i.decode() for i in status.children.keys() ]
 #        if now - lookup(status, [node, "last_update"]) > 3600
 #      ]


