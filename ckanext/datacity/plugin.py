import ckan.plugins as plugins
from ckan.plugins.toolkit import add_template_directory, add_public_directory, add_resource
from . import helpers


class DatacityPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IGroupController)

    def update_config(self, config):
        add_template_directory(config, 'templates')
        add_public_directory(config, 'public')
        add_resource('fanstatic', 'datacity')

    def get_helpers(self):
        return {
            "setting": helpers.get_setting,
            "datacity_settings_edit_link": helpers.get_datacity_settings_edit_link,
            "color": helpers.get_color,
            "site_title": helpers.get_site_title,
            "homepage_groups": helpers.get_homepage_groups,
            "popular_datasets": helpers.get_popular_datasets,
            "last_updated_datasets": helpers.get_last_updated_datasets,
        }

    def read(self, entity):
        pass

    def create(self, entity):
        pass

    def edit(self, entity):
        helpers.plugin_edit_clear_settings_cache(entity)

    def delete(self, entity):
        pass

    def before_view(self, pkg_dict):
        return pkg_dict
