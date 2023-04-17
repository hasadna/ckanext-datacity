import ckan.plugins as plugins
from ckan.plugins.toolkit import add_template_directory, add_public_directory, add_resource, get_action
from . import helpers


class DatacityPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IGroupController)
    plugins.implements(plugins.IOrganizationController)
    plugins.implements(plugins.IPackageController)
    plugins.implements(plugins.IResourceController)

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
            "gravatar_accessibility": helpers.gravatar_accessibility,
            "update_organization_lang": helpers.update_organization_lang,
            "get_facet_list_items": helpers.get_facet_list_items,
            "get_group_display_name_lang": helpers.get_group_display_name_lang,
            "get_group_description_lang": helpers.get_group_description_lang,
            "get_dataset_name_lang": helpers.get_dataset_name_lang,
            'filter_enabled_locales': helpers.filter_enabled_locales,
            "is_scheming_field_lang_support_enabled": helpers.is_scheming_field_lang_support_enabled,
        }

    def read(self, entity):
        pass

    def create(self, entity):
        helpers.plugin_edit_clear_settings_cache(entity)

    def edit(self, entity):
        helpers.plugin_edit_clear_settings_cache(entity)

    def delete(self, entity):
        helpers.plugin_edit_clear_settings_cache(entity)

    def before_view(self, pkg_dict):
        lang = helpers.get_short_lang()
        if lang != 'he':
            if pkg_dict.get('type') == 'organization':
                for e in pkg_dict.get('extras', []):
                    if e.get('key') == 'title_{}'.format(lang) and e.get('value'):
                        pkg_dict['title'] = pkg_dict['display_name'] = e['value']
                    if e.get('key') == 'description_{}'.format(lang) and e.get('value'):
                        pkg_dict['description'] = e['value']
            elif pkg_dict.get('type') == 'group':
                for e in pkg_dict.get('extras', []):
                    if e.get('key') == 'title_{}'.format(lang) and e.get('value'):
                        pkg_dict['title'] = pkg_dict['display_name'] = e['value']
                    if e.get('key') == 'description_{}'.format(lang) and e.get('value'):
                        pkg_dict['description'] = e['value']
            elif pkg_dict.get('type') == 'dataset':
                org_id = pkg_dict.get('organization', {}).get('id')
                if org_id:
                    org = get_action('organization_show')(data_dict={
                        'id': pkg_dict['organization']['name']
                    })
                    title_lang = org.get('title_{}'.format(lang))
                    if title_lang:
                        pkg_dict['organization']['title'] = title_lang
                title_lang = pkg_dict.get('title_{}'.format(lang))
                if title_lang:
                    pkg_dict['title'] = title_lang
                for r in pkg_dict.get('resources', []):
                    name_lang = r.get('name_{}'.format(lang))
                    if name_lang:
                        r['name'] = name_lang
                    description_lang = r.get('description_{}'.format(lang))
                    if description_lang:
                        r['description'] = description_lang
                for group in pkg_dict.get('groups', []):
                    group = get_action('group_show')(data_dict={
                        'id': group['name']
                    })
                    title_lang = group.get('title_{}'.format(lang))
                    if title_lang:
                        group['title'] = title_lang
                    description_lang = group.get('description_{}'.format(lang))
                    if description_lang:
                        group['description'] = description_lang
        # print('-----------')
        # print(pkg_dict.get('type'))
        # print(pkg_dict)
        # print('-----------')
        return pkg_dict

    def after_create(self, context, pkg_dict):
        pass

    def after_update(self, context, pkg_dict):
        pass

    def after_delete(self, context, pkg_dict):
        pass

    def after_show(self, context, pkg_dict):
        pass

    def before_show(self, resource_dict):
        pass

    def before_search(self, search_params):
        return search_params

    def after_search(self, search_results, search_params):
        return search_results

    def before_index(self, pkg_dict):
        return pkg_dict