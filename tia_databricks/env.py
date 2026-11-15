import logging

from environs import Env

_env = Env(expand_vars=True)

# ===============================================
#           Logging
# ===============================================
# LOG_LEVEL - The logging level for the family.
LOG_LEVEL = _env.log_level("LOG_LEVEL", logging.INFO)
