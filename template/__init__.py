
class TemplateSensor:
    def __init__(self, entity, sources, template, helper):
        self.next_poll_trigger = None
        self.entity = entity
        self.sources = sources
        self.template = template
        self.helper = helper
        for entity in self.sources:
            self.helper.hass.add_callback(self.update, entity)

    def update(self, state = None, attributes = None):
        source_state = dict([
            (entity, self.helper.hass[entity])
            for entity in self.sources
        ])
        sensor_state = self.template(source_state)
        print("{} <- {}".format(self.entity, sensor_state))
        self.helper.hass.post_update(
            self.entity,
            sensor_state,
            attributes = {}
        )

