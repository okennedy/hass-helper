
from tasklib import TaskWarrior
from notify import NotificationGenerator, Notification
from datetime import date, datetime, timedelta, timezone
import re


class TaskWarriorNotifier(NotificationGenerator):
  """
  Generate notifications based on TaskWarrior tasks (https://taskwarrior.org/)

  - filter(dict, optional):
      Only display tasks matching a specific set of conditions.  See 
      https://tasklib.readthedocs.io/en/latest/#filtering for filtering
      syntax (dict fields are passed directly as arguments to tasklib's 
      .filter function).
  - due_cutoff(int, optional):
      Only display tasks with a due date in the next `due_cutoff` days.
      Defaults to 10 days.
  - icon(str, optional)
      The icon to associate with the notification
  """

  def __init__(self, **kwargs):
    super(TaskWarriorNotifier, self).__init__(
      poll_interval = kwargs.get("poll_interval", 5*60)
    )
    self.filter = kwargs.get("filter", None)
    self.due_cutoff = kwargs.get("cutoff", 10)
    self.icon = kwargs.get("icon", "office/notes")

  def update(self, hass):
    tw = TaskWarrior()
    tasks = tw.tasks
    # print("Tasks: {}".format(tasks))
    # print("Filter: {}".format(self.filter))
    if self.filter is not None:
      tasks = tasks.filter(**self.filter)
    else:
      tasks = tasks.all()
    now = datetime.now(timezone.utc)
    self.notifications = [ 
      Notification(
        body = re.sub(" +\\(.+", "", task['description']),
        priority = -days_until_due,
        status = "warning" if days_until_due < 0 else "info",
        icon = self.icon
      )
      for task in tasks
      for days_until_due in [((task['due'] if task['due'] is not None else now) - now).days]
      if days_until_due < self.due_cutoff
    ]
