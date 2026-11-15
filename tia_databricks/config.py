from importlib.metadata import version

from . import env

# ===============================================
#           General
# ===============================================
artifact_name = __package__
artifact_version = version(artifact_name)

# ===============================================
#           Logging
# ===============================================
log_level = env.LOG_LEVEL
