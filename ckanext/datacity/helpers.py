from ckan.logic import NotFound
import json
from ckan.common import config
from .constants import (
    SETTINGS_REDIS_KEY_PREFIX,
    HOMEPAGE_GROUPS_REDIS_KEY, HOMEPAGE_GROUPS_REDIS_KEY_EXPIRES_SECONDS,
    HOMEPAGE_LAST_UPDATED_DATASETS_REDIS_KEY, HOMEPAGE_LAST_UPDATED_DATASETS_REDIS_KEY_EXPIRES_SECONDS,
    HOMEPAGE_POPULAR_DATASETS_REDIS_KEY, HOMEPAGE_POPULAR_DATASETS_REDIS_KEY_EXPIRES_SECONDS
)
from ckan.lib.redis import connect_to_redis
from ckan.plugins.toolkit import get_action
from ckan.lib.helpers import lang


def redis_cache(key, key_ex):
    def _decorator(get_value):
        def _wrapper():
            conn = connect_to_redis()
            raw_value = conn.get(key)
            if raw_value is None:
                value = get_value()
                conn.set(key, json.dumps(value), ex=key_ex)
                return value
            else:
                return json.loads(raw_value)
        return _wrapper
    return _decorator


def get_setting(setting, default=None):
    value = None
    if config.get(u'datacity.settings_group_id'):
        conn = connect_to_redis()
        key = "%s:%s" % (SETTINGS_REDIS_KEY_PREFIX, config[u'ckan.site_id'])
        raw_value = conn.get(key)
        if raw_value is None:
            try:
                value = get_action("group_show")(data_dict={
                    "id": config[u'datacity.settings_group_id'],
                    "include_extras": True, "include_dataset_count": False, "include_users": False,
                    "include_groups": False, "include_tags": False, "include_followers": False
                })
            except NotFound:
                value = {}
            conn.set(key, json.dumps(value))
            value = value.get(setting)
        else:
            value = json.loads(raw_value).get(setting)
    if value:
        value = unicode(value).strip()
    if not value and default != None:
        return default
    else:
        return value


def get_color(color):
    default = {
        "top_header_background_color": "ffffff",
        "menu_background_color": "ffffff",
        "menu_text_color": "1c4f7c",
        "menu_highlight_color": "f1ae89",
        "homepage_title_text_color": "1c4f7c",
        "homepage_title_background_color": lambda: get_color("menu_background_color"),
        "homepage_title_border_color": "",
        "homepage_groups_background_color": "1c4f7c",
        "homepage_groups_text_color": "ffffff",
        "homepage_groups_inner_background_color": "ffffff",
        "homepage_groups_inner_hover_background_color": "d7d7d7",
        "homepage_groups_inner_text_color": "13699e",
        "footer_background_color": "1c4f7c",
        "homepage_datasets_background_color": lambda: get_color("top_header_background_color"),
        "homepage_datasets_button_hover_background_color": "d7d7d7",
        "homepage_datasets_text_color": "#1c4f7c",
        "footer_separator_color": "#e5e5e5"
    }.get(color, "#000000")
    value = get_setting(color, default() if callable(default) else default)
    if not value.startswith("#"):
        value = "#" + value
    return value


def get_site_title():
    return get_setting('site_title_' + lang(), get_setting('site_title_he', config.get(u'ckan.site_title', 'CKAN')))


def get_datacity_settings_edit_link():
    if config.get(u'datacity.settings_group_id'):
        return '/settings/edit/%s' % config.get(u'datacity.settings_group_id')
    else:
        return None


def plugin_edit_clear_settings_cache(entity):
    if config.get(u'datacity.settings_group_id') and entity.type == "settings" and (entity.name == config[u'datacity.settings_group_id'] or entity.id == config[u'datacity.settings_group_id']):
        conn = connect_to_redis()
        key = "%s:%s" % (SETTINGS_REDIS_KEY_PREFIX, config[u'ckan.site_id'])
        conn.delete(key)
        conn.delete(HOMEPAGE_POPULAR_DATASETS_REDIS_KEY)
        conn.delete(HOMEPAGE_LAST_UPDATED_DATASETS_REDIS_KEY)
    elif entity.type == "group" or entity.type == "dataset":
        conn = connect_to_redis()
        for key in conn.keys("ckanext:datacity:homepage:*"):
            conn.delete(key)


@redis_cache(HOMEPAGE_GROUPS_REDIS_KEY, HOMEPAGE_GROUPS_REDIS_KEY_EXPIRES_SECONDS)
def get_homepage_groups():
    return get_action("group_list")(data_dict={
        "all_fields": True,
        "include_dataset_count": True,
        "sort": "title"
    })


@redis_cache(HOMEPAGE_POPULAR_DATASETS_REDIS_KEY, HOMEPAGE_POPULAR_DATASETS_REDIS_KEY_EXPIRES_SECONDS)
def get_popular_datasets():
    return get_action("package_search")(data_dict={
        "sort": "views_recent desc",
        "rows": int(get_setting("homepage_featured_packages_num", "3")),
    })["results"]


@redis_cache(HOMEPAGE_LAST_UPDATED_DATASETS_REDIS_KEY, HOMEPAGE_LAST_UPDATED_DATASETS_REDIS_KEY_EXPIRES_SECONDS)
def get_last_updated_datasets():
    return get_action("package_search")(data_dict={
        "sort": "metadata_modified desc",
        "rows": int(get_setting("homepage_featured_packages_num", "3")),
    })["results"]


def gravatar_accessibility(html):
    return html.replace('alt="Gravatar"', 'alt=""')


def get_short_lang():
    return {
        'en_US': 'en',
        'ar': 'ar'
    }.get(lang(), 'he')


def update_organization_lang(organization):
    lng = get_short_lang()
    if organization.get('title_' + lng):
        organization['title'] = organization['title_' + lng]
    if organization.get('description_' + lng):
        organization['description'] = organization['description_' + lng]


def get_facet_list_items(name, items):
    lng = get_short_lang()
    if lng != 'he':
        if name in ('organization', 'groups'):
            for item in items:
                org_id = item.get('name')
                if org_id:
                    org = get_action('{}_show'.format(name if name == 'organization' else 'group'))(data_dict={
                        'id': org_id
                    })
                    title_lang = org.get('title_{}'.format(lng))
                    if title_lang:
                        item['display_name'] = title_lang
    # print(name)
    # print(items)
    return items


def get_group_display_name_lang(group, display_name):
    lng = get_short_lang()
    if lng == 'he':
        return display_name
    else:
        return get_action('group_show')(data_dict={'id': group['name']}).get('title_{}'.format(lng), display_name)


def get_group_description_lang(group, description):
    lng = get_short_lang()
    if lng == 'he':
        return description
    else:
        return get_action('group_show')(data_dict={'id': group['name']}).get('description_{}'.format(lng), description)


def get_dataset_name_lang(dataset, name):
    lng = get_short_lang()
    if lng == 'he':
        return name
    else:
        return get_action('package_show')(data_dict={'id': dataset['name']}).get('title_{}'.format(lng), name)


def filter_enabled_locales(locales):
    for locale in locales:
        if locale.identifier == 'he':
            yield locale
        elif locale.identifier == 'en_US':
            if get_setting('english_language_support') == 'yes':
                yield locale
        elif locale.identifier == 'ar':
            if get_setting('arabic_language_support') == 'yes':
                yield locale


def is_scheming_field_lang_support_enabled(field):
    if field.get('lang_support'):
        if field['lang_support'] == 'english':
            return get_setting('english_language_support') == 'yes'
        elif field['lang_support'] == 'arabic':
            return get_setting('arabic_language_support') == 'yes'
        else:
            return False
    else:
        return True
