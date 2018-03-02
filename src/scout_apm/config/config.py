from __future__ import absolute_import

import logging
import os
import platform

logger = logging.getLogger(__name__)


class ScoutConfig():
    """
    Configuration object for the ScoutApm agent.

    Contains a list of configuration "layers". When a configuration key is
    looked up, each layer is asked in turn if it knows the value. The first one
    to answer affirmatively returns the value.
    """
    def __init__(self):
        self.layers = [
            ScoutConfigEnv(),
            ScoutConfigDefaults(),
            ScoutConfigNull()]
        self.log()

    def value(self, key):
        return self.locate_layer_for_key(key).value(key)

    def locate_layer_for_key(self, key):
        for layer in self.layers:
            if layer.has_config(key):
                return layer

    def log(self):
        logger.debug('Configuration Loaded:')
        for key in self.known_keys():
            layer = self.locate_layer_for_key(key)
            logger.debug('{:9}: {} = {}'.format(
                layer.name(),
                key,
                layer.value(key)))

    def known_keys(self):
        return [
            'core_agent_dir',
            'core_agent_download',
            'core_agent_launch',
            'core_agent_version',
            'download_url',
            'git_sha',
            'log_level',
            'name',
            'key',
            'socket_path'
        ]

    def core_agent_full_name(self):
        return 'scout_apm_core-{version}-{platform}-{arch}'.format(
                version=self.value('core_agent_version'),
                platform=self.platform(),
                arch=self.arch())

    @classmethod
    def platform(cls):
        system_name = platform.system()
        if system_name == 'Linux':
            return 'linux'
        elif system_name == 'Darwin':
            return 'darwin'
        else:
            return 'unknown'

    @classmethod
    def arch(cls):
        arch = platform.machine()
        if arch == 'i686':
            return 'i686'
        elif arch == 'x86_64':
            return 'x86_64'
        else:
            return 'unknown'


class ScoutConfigEnv():
    """
    Reads configuration from environment by prefixing the key
    requested with "SCOUT_"

    Example: the `log_level` config looks for SCOUT_LOG_LEVEL
    environment variable
    """

    def name(self):
        return 'ENV'

    def has_config(self, key):
        env_key = self.modify_key(key)
        return env_key in os.environ

    def value(self, key):
        env_key = self.modify_key(key)
        return os.environ[env_key]

    def modify_key(self, key):
        env_key = ('SCOUT_' + key).upper()
        return env_key


class ScoutConfigDefaults():
    """
    Provides default values for important configurations
    """

    def name(self):
        return 'Defaults'

    def __init__(self):
        self.core_agent_dir = '/tmp/scout_apm_core'
        self.core_agent_version = 'latest'
        self.defaults = {
                'core_agent_dir': self.core_agent_dir,
                'core_agent_download': True,
                'core_agent_launch': True,
                'core_agent_version': self.core_agent_version,
                'download_url': 'https://download.scoutapp.com/scout_apm_core',
                'git_sha': '',
                'key': '',
                'log_level': 'info',
                'name': '',
                'socket_path': '{}/scout_apm_core-{}-{}-{}/core-agent.sock'.format(self.core_agent_dir,
                                                                                   self.core_agent_version,
                                                                                   ScoutConfig.platform(),
                                                                                   ScoutConfig.arch())
        }

    def has_config(self, key):
        return key in self.defaults

    def value(self, key):
        return self.defaults[key]


# Always returns None to any key
class ScoutConfigNull():
    """
    Always answers that a key is present, but the value is None

    Used as the last step of the layered configuration.
    """

    def name(self):
        return 'Null'

    def has_config(self, key):
        return True

    def value(self, key):
        return None