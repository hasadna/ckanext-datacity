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

    def _func(get_value):
        conn = connect_to_redis()
        raw_value = conn.get(key)
        if raw_value is None:
            value = get_value()
            conn.set(key, json.dumps(value), ex=key_ex)
            return value
        else:
            return json.loads(raw_value)

    return _func


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
    if not value and default != None:
        return default
    else:
        return value


def get_color(color):
    value = get_setting(color, {
        "top_header_background_color": "d6edd2",
        "menu_background_color": "d6edd2",
        "menu_text_color": "05396b",
        "menu_highlight_color": "eeeeee",
        "homepage_title_text_color": "edf5e1",
        "homepage_groups_background_color": "005d7a",
        "homepage_groups_text_color": "edf5e1",
        "footer_background_color": "05386b",
    }.get(color, "#000000"))
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
        "rows": 10,
    })["results"]


@redis_cache(HOMEPAGE_LAST_UPDATED_DATASETS_REDIS_KEY, HOMEPAGE_LAST_UPDATED_DATASETS_REDIS_KEY_EXPIRES_SECONDS)
def get_last_updated_datasets():
    return get_action("package_search")(data_dict={
        "sort": "metadata_modified desc",
        "rows": 10,
    })["results"]
