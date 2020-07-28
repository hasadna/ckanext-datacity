import ckan.plugins as plugins
from ckan.plugins.toolkit import add_template_directory, add_public_directory, add_resource, get_action


PLUGIN_CACHE = {}


class DatacityPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    def update_config(self, config):
        add_template_directory(config, 'templates')
        add_public_directory(config, 'public')
        add_resource('fanstatic', 'datacity')
