from unittest.mock import MagicMock, patch

import pytest
from tiozin.exceptions import RequiredArgumentError

from tia_databricks import DatabricksExternalRunner


# ============================================================================
# Testing DatabricksExternalRunner initialization
# ============================================================================
def test_external_runner_should_store_connection_parameters():
    # Arrange
    catalog = "fake_catalog"
    host = "https://fake-workspace.cloud.databricks.com"
    client_id = "fake-client-id"
    client_secret = "fake-client-secret"
    scope = "fake-scope"
    format = "iceberg"

    # Act
    runner = DatabricksExternalRunner(
        catalog=catalog,
        host=host,
        client_id=client_id,
        client_secret=client_secret,
        scope=scope,
        format=format,
    )

    # Assert
    actual = (
        runner.catalog,
        runner.host,
        runner.client_id,
        runner.client_secret,
        runner.scope,
        runner.format,
    )
    expected = (
        "fake_catalog",
        "https://fake-workspace.cloud.databricks.com",
        "fake-client-id",
        "fake-client-secret",
        "fake-scope",
        "iceberg",
    )
    assert actual == expected


def test_external_runner_should_default_scope_and_format():
    # Act
    runner = DatabricksExternalRunner(
        catalog="fake_catalog",
        host="https://fake-workspace.cloud.databricks.com",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
    )

    # Assert
    actual = (
        runner.scope,
        runner.format,
    )
    expected = (
        "unity-catalog",
        "delta",
    )
    assert actual == expected


def test_external_runner_should_trim_connection_parameters():
    # Arrange
    catalog = "  fake_catalog  "
    host = "  https://fake-workspace.cloud.databricks.com  "
    client_id = "  fake-client-id  "
    client_secret = "  fake-client-secret  "
    scope = "  fake-scope  "

    # Act
    runner = DatabricksExternalRunner(
        catalog=catalog,
        host=host,
        client_id=client_id,
        client_secret=client_secret,
        scope=scope,
    )

    # Assert
    actual = (
        runner.catalog,
        runner.host,
        runner.client_id,
        runner.client_secret,
        runner.scope,
    )
    expected = (
        "fake_catalog",
        "https://fake-workspace.cloud.databricks.com",
        "fake-client-id",
        "fake-client-secret",
        "fake-scope",
    )
    assert actual == expected


@pytest.mark.parametrize("format", ["ICEBERG", "  iceberg  ", " Iceberg "])
def test_external_runner_should_normalize_format(format: str):
    # Act
    runner = DatabricksExternalRunner(
        catalog="fake_catalog",
        host="https://fake-workspace.cloud.databricks.com",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
        format=format,
    )

    # Assert
    actual = runner.format
    expected = "iceberg"
    assert actual == expected


@pytest.mark.parametrize(
    "host",
    [
        "https://fake-workspace.cloud.databricks.com/",
        "  https://fake-workspace.cloud.databricks.com/  ",
    ],
)
def test_external_runner_should_strip_host_trailing_slash(host: str):
    # Act
    runner = DatabricksExternalRunner(
        catalog="fake_catalog",
        host=host,
        client_id="fake-client-id",
        client_secret="fake-client-secret",
    )

    # Assert
    actual = runner.host
    expected = "https://fake-workspace.cloud.databricks.com"
    assert actual == expected


def test_external_runner_should_derive_token_url_from_host():
    # Act
    runner = DatabricksExternalRunner(
        catalog="fake_catalog",
        host="  https://fake-workspace.cloud.databricks.com/  ",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
    )

    # Assert
    actual = runner.token_url
    expected = "https://fake-workspace.cloud.databricks.com/oidc/v1/token"
    assert actual == expected


@pytest.mark.parametrize("value", [None, ""])
@pytest.mark.parametrize("field", ["catalog", "host", "client_id", "client_secret"])
def test_external_runner_should_raise_required_argument_error_when_argument_is_missing(
    field: str, value: str | None
):
    # Arrange
    arguments = {
        "catalog": "fake_catalog",
        "host": "https://fake-workspace.cloud.databricks.com",
        "client_id": "fake-client-id",
        "client_secret": "fake-client-secret",
    }
    arguments[field] = value

    # Act & Assert
    with pytest.raises(RequiredArgumentError, match=field):
        DatabricksExternalRunner(**arguments)


# ============================================================================
# Testing DatabricksExternalRunner setup
# ============================================================================
@patch("tiozin.api.tiozin.current_context")
@patch("tiozin.family.tio_spark.runners.spark_runner.SparkSession")
def test_setup_should_configure_unity_catalog_for_delta(
    spark_session: MagicMock, _current_context: MagicMock
):
    # Arrange
    builder = spark_session.builder
    builder.appName.return_value = builder
    builder.config.return_value = builder

    # Act
    runner = DatabricksExternalRunner(
        catalog="fake_catalog",
        host="https://fake-workspace.cloud.databricks.com",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
    )
    with runner():
        pass

    # Assert
    actual = dict(c.args for c in builder.config.call_args_list)
    expected = {
        "spark.sql.session.timeZone": "UTC",
        "spark.sql.adaptive.enabled": "true",
        "spark.jars.packages": "",
        "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
        "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        "spark.sql.catalog.fake_catalog": "io.unitycatalog.spark.UCSingleCatalog",
        "spark.sql.catalog.fake_catalog.uri": "https://fake-workspace.cloud.databricks.com",
        "spark.sql.catalog.fake_catalog.auth.type": "oauth",
        "spark.sql.catalog.fake_catalog.auth.oauth.uri": (
            "https://fake-workspace.cloud.databricks.com/oidc/v1/token"
        ),
        "spark.sql.catalog.fake_catalog.auth.oauth.clientId": "fake-client-id",
        "spark.sql.catalog.fake_catalog.auth.oauth.clientSecret": "fake-client-secret",
        "spark.sql.catalog.fake_catalog.auth.oauth.scope": "unity-catalog",
        "spark.hadoop.fs.s3.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
        "spark.sql.defaultCatalog": "fake_catalog",
    }
    assert actual == expected


@patch("tiozin.api.tiozin.current_context")
@patch("tiozin.family.tio_spark.runners.spark_runner.SparkSession")
def test_setup_should_configure_iceberg_rest_catalog_for_iceberg(
    spark_session: MagicMock, _current_context: MagicMock
):
    # Arrange
    builder = spark_session.builder
    builder.appName.return_value = builder
    builder.config.return_value = builder

    # Act
    runner = DatabricksExternalRunner(
        catalog="fake_catalog",
        host="https://fake-workspace.cloud.databricks.com",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
        format="iceberg",
    )
    with runner():
        pass

    # Assert
    actual = dict(c.args for c in builder.config.call_args_list)
    expected = {
        "spark.sql.session.timeZone": "UTC",
        "spark.sql.adaptive.enabled": "true",
        "spark.jars.packages": "",
        "spark.sql.extensions": (
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
        ),
        "spark.sql.catalog.fake_catalog": "org.apache.iceberg.spark.SparkCatalog",
        "spark.sql.catalog.fake_catalog.type": "rest",
        "spark.sql.catalog.fake_catalog.uri": (
            "https://fake-workspace.cloud.databricks.com/api/2.1/unity-catalog/iceberg-rest"
        ),
        "spark.sql.catalog.fake_catalog.warehouse": "fake_catalog",
        "spark.sql.catalog.fake_catalog.rest.auth.type": "oauth2",
        "spark.sql.catalog.fake_catalog.oauth2-server-uri": (
            "https://fake-workspace.cloud.databricks.com/oidc/v1/token"
        ),
        "spark.sql.catalog.fake_catalog.credential": "fake-client-id:fake-client-secret",
        "spark.sql.catalog.fake_catalog.scope": "unity-catalog",
        "spark.sql.defaultCatalog": "fake_catalog",
    }
    assert actual == expected


@patch("tiozin.api.tiozin.current_context")
@patch("tiozin.family.tio_spark.runners.spark_runner.SparkSession")
def test_setup_should_keep_options_as_spark_conf(
    spark_session: MagicMock, _current_context: MagicMock
):
    # Arrange
    builder = spark_session.builder
    builder.appName.return_value = builder
    builder.config.return_value = builder
    options = {
        "spark.sql.shuffle.partitions": "200",
        "spark.sql.ansi.enabled": "true",
    }

    # Act
    runner = DatabricksExternalRunner(
        catalog="fake_catalog",
        host="https://fake-workspace.cloud.databricks.com",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
        **options,
    )
    with runner():
        pass

    # Assert
    actual = dict(c.args for c in builder.config.call_args_list)
    assert options.items() <= actual.items()


@patch("tiozin.api.tiozin.current_context")
@patch("tiozin.family.tio_spark.runners.spark_runner.SparkSession")
def test_setup_should_reuse_session_when_session_already_exists(
    spark_session: MagicMock, _current_context: MagicMock
):
    # Arrange
    builder = spark_session.builder
    builder.appName.return_value = builder
    builder.config.return_value = builder

    # Act
    runner = DatabricksExternalRunner(
        catalog="fake_catalog",
        host="https://fake-workspace.cloud.databricks.com",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
    )
    with runner():
        with runner():
            pass

    # Assert
    builder.getOrCreate.assert_called_once()
