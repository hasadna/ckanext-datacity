from ckan.logic import NotFound
import json
from ckan.common import config
from .constants import SETTINGS_REDIS_KEY_PREFIX
from ckan.lib.redis import connect_to_redis
from ckan.plugins.toolkit import get_action
from ckan.lib.helpers import _make_menu_item
from ckan.common import _


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


def plugin_edit_clear_settings_cache(entity):
    if config.get(u'datacity.settings_group_id') and entity.type == "settings" and (entity.name == config[u'datacity.settings_group_id'] or entity.id == config[u'datacity.settings_group_id']):
        conn = connect_to_redis()
        key = "%s:%s" % (SETTINGS_REDIS_KEY_PREFIX, config[u'ckan.site_id'])
        conn.delete(key)
