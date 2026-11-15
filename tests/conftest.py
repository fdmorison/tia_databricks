import uuid
from collections.abc import Generator
from typing import Any

import pytest
from databricks.sdk.core import Config
from pyspark.sql import SparkSession

from tests import env

# --------------------------------------------------
# Spark
# --------------------------------------------------


@pytest.fixture(scope="session")
def spark_session(tmp_path_factory: pytest.TempPathFactory) -> Generator[SparkSession, Any, None]:
    with pytest.MonkeyPatch.context() as mp:
        mp.delenv("SPARK_HOME", raising=False)
        builder: SparkSession.Builder = SparkSession.builder
        spark = (
            builder.appName("test")
            .config("spark.sql.session.timeZone", "UTC")
            .config("spark.sql.adaptive.enabled", "true")
            .config("spark.sql.warehouse.dir", tmp_path_factory.mktemp(str(uuid.uuid4())))
            .getOrCreate()
        )
    yield spark
    spark.stop()


@pytest.fixture(scope="session")
def databricks_connect_session() -> Generator[SparkSession, Any, None]:
    from databricks.connect import DatabricksSession

    sdk_config = Config(
        host=env.DATABRICKS_HOST,
        cluster_id=env.DATABRICKS_CLUSTER_ID,
        client_id=env.DATABRICKS_CLIENT_ID,
        client_secret=env.DATABRICKS_CLIENT_SECRET,
    )
    spark = DatabricksSession.builder.sdkConfig(sdk_config).getOrCreate()
    spark.conf.set("spark.sql.session.timeZone", "UTC")
    spark.conf.set("spark.sql.adaptive.enabled", "true")
    yield spark
    spark.stop()


# --------------------------------------------------
# Taxonomy
# --------------------------------------------------


@pytest.fixture()
def fake_domain() -> dict:
    return dict(
        org="acme",
        region="latam",
        domain="ecommerce",
        subdomain="checkout",
        layer="raw",
        product="sales",
        model="orders",
    )
