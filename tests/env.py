import logging

from environs import Env

_env = Env(expand_vars=True)

# ===============================================
#           Logging
# ===============================================
LOG_LEVEL = logging.WARNING

# ===============================================
#           Databricks Connect
# ===============================================
DATABRICKS_HOST = _env.str("DATABRICKS_HOST", None)
DATABRICKS_CLUSTER_ID = _env.str("DATABRICKS_CLUSTER_ID", None)
DATABRICKS_CLIENT_ID = _env.str("DATABRICKS_CLIENT_ID", None)
DATABRICKS_CLIENT_SECRET = _env.str("DATABRICKS_CLIENT_SECRET", None)
