import logging
from config.configure import Config

logger = logging.getLogger("peng_finance")
logger.setLevel(Config.LOG_LEVEL)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)
