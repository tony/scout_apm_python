from __future__ import absolute_import

# Python Modules
import logging
from os import getpid

from scout_apm.core.config.config import ScoutConfig
from scout_apm.core.context import AgentContext
from scout_apm.core.core_agent_manager import CoreAgentManager
from scout_apm.core.instrument_manager import InstrumentManager
from scout_apm.core.metadata import AppMetadata

logger = logging.getLogger(__name__)


def install():
    config = ScoutConfig()
    context = AgentContext.build(config=config)

    if not context.config.value('monitor'):
        logger.info("APM Not Launching on PID: %s - Configuration 'monitor' is not true", getpid())
        return False

    logger.debug('APM Launching on PID: %s', getpid())
    CoreAgentManager().launch()
    AppMetadata.report()
    AgentContext.socket().stop()
    return True
