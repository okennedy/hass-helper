from HassHelper import HassHelper
from notify.taskwarrior import TaskWarriorNotifier
from notify.caldav import CalDavNotifier
from notify.time import WeekdayNotifier
from notify.state import StateNotifier, SensorOfflineNotifier

"""
  A simple example configuration for Hass Helper.  See HassHelper.py for 
  more details.

  This example creates a new sensor named status.housewide that maintains 
  a set of notifications.  The sensor state is the number of notifications
  and the `notifications` attribute contains a list of objects with the fields:
    - body      : Text describing the notification
    - status    : One of 'info', 'warning', or 'danger'
    - priority  : A number used to sort the notifications (higher = earlier)
    - action    : Unused
    - icon      : Used to identify an image to associate with the notification
"""

print("Starting HassHelper")

##
## The main role of main.py is to configure a HassHelper object
## and put it into a worker loop.
## 
## Make sure to set an API key.  Support for accounts is not implemented yet.
##
helper = HassHelper(
  host    = "http://<YOUR SERVER HERE>", 
  api_key = "<YOUR HASS AUTH TOKEN HERE>",
  notification_entity = "status.housewide"
)

##
## TaskWarrior (https://taskwarrior.org/) is a GTD-style TODO list manager
##
## The following example adds notifications for pending tasks due in the next 10 days
## tagged +home.  The filter parameter is passed directly to tasklib 
## (see https://pypi.org/project/tasklib/)
##
helper.notifications.add(
  TaskWarriorNotifier(
    filter = {
      "status" : "pending",
      "tags__contains" : ['home']
    },
    cutoff = 10 # days
  )
)

##
## CalDav is a protocol for scheduling.  
##
## The following example adds a notification for every event occurring within the next 
## week appearing in the calendar <Calendar Name Including Spaces>
## 
helper.notifications.add(
  CalDavNotifier(
    url      = "http://<CALDAV SERVER HERE>",
    calendars= ["<Calendar Name Including Spaces>"],
    user     = "<USERNAME>",
    password = "<PASSWORD>",
    window   = 604800 # seconds = 1 week
  )
)

## 
## WeekdayNotifier brings up a notification on one specific day of the week
## 
## The following example adds a notification to walk out the trash every Thursday
##
helper.notifications.add(
  WeekdayNotifier(
    day_of_week = 3,   # Thursday (0 = Monday, 6 = Sunday)
    message     = "Walk out the trash",
    status      = "warning",
    icon        = "ecology/recycling-1"
  )
)

##
## State Notifier triggers a notification when a specific condition is met.
##

##
## The following example displays a notification whenever sensor.garage_door != "closed"
## 
helper.notifications.add(
  StateNotifier(
    entities = ["sensor.garage_door"],
    icon    = "transportation/car",
    ## When to trigger the notification
    trigger = lambda hass: hass["sensor.garage_door"].state != "closed",
    ## A procedure to generate the notification
    message = lambda hass: "The garage door is {}".format(hass["sensor.garage_door"].state),
  )
)


##
## The following example displays a notification whenever one of two sump well sensors
## triggers. (sensor.sump_liquid_level < 1600 or binary_sensor.sump_well_overflow == "on")
##   
def sump_well_overflow(hass):
  analog_overflow = float(hass["sensor.sump_liquid_level"].state) < 1600
  digital_overflow = hass["binary_sensor.sump_well_overflow"].state == "on"
  return analog_overflow or digital_overflow

helper.notifications.add(
  StateNotifier(
    entities = ["sensor.sump_liquid_level", "binary_sensor.sump_well_overflow"],
    icon     = "ecology/water-tap",
    status   = "danger",
    ## When to trigger the notification
    trigger  = sump_well_overflow,
    ## A procedure to generate the notification
    message  = lambda hass: "The sump pump might be down",
  )
)

## 
## SensorOffline notification triggers a warning whenever the last_updated attribute
## of a specific sensor falls behind the current time more than a specified threshold.
## 
## The following example configures 5 entities with a timeout of 5 hours.
##
helper.notifications.add(
  SensorOfflineNotifier(
    entities = [
      ("Office sensors", "sensor.office_temperature"),
      ("Armory sensors", "sensor.armory_temperature"),
      ("Furnace area sensors", "sensor.furnace_humidity"), # Use humidity sensor... temperature down there is too stable!
      ("Sump Well area sensors", "sensor.sump_liquid_level"),
      ("Garage sensors", "sensor.garage_temperature")
    ],
    timeout = 5*60*60 # seconds = 5 hours
  )
)

print("Starting Loop")
helper.run()