from unittest.mock import MagicMock, call, patch

import pytest
from tiozin.exceptions import RequiredArgumentError

from tia_databricks import DatabricksConnectRunner


# ============================================================================
# Testing DatabricksConnectRunner initialization
# ============================================================================
def test_connect_runner_should_store_connection_parameters():
    # Arrange
    host = "https://fake-workspace.cloud.databricks.com"
    cluster_id = "0000-000000-fakeclus"
    client_id = "fake-client-id"
    client_secret = "fake-client-secret"

    # Act
    runner = DatabricksConnectRunner(
        host=host,
        cluster_id=cluster_id,
        client_id=client_id,
        client_secret=client_secret,
    )

    # Assert
    actual = (
        runner.host,
        runner.cluster_id,
        runner.client_id,
        runner.client_secret,
    )
    expected = (
        "https://fake-workspace.cloud.databricks.com",
        "0000-000000-fakeclus",
        "fake-client-id",
        "fake-client-secret",
    )
    assert actual == expected


def test_connect_runner_should_trim_connection_parameters():
    # Arrange
    host = "  https://fake-workspace.cloud.databricks.com  "
    cluster_id = "  0000-000000-fakeclus  "
    client_id = "  fake-client-id  "
    client_secret = "  fake-client-secret  "

    # Act
    runner = DatabricksConnectRunner(
        host=host,
        cluster_id=cluster_id,
        client_id=client_id,
        client_secret=client_secret,
    )

    # Assert
    actual = (
        runner.host,
        runner.cluster_id,
        runner.client_id,
        runner.client_secret,
    )
    expected = (
        "https://fake-workspace.cloud.databricks.com",
        "0000-000000-fakeclus",
        "fake-client-id",
        "fake-client-secret",
    )
    assert actual == expected


@pytest.mark.parametrize(
    "host",
    [
        "https://fake-workspace.cloud.databricks.com/",
        "  https://fake-workspace.cloud.databricks.com/  ",
    ],
)
def test_connect_runner_should_strip_host_trailing_slash(host: str):
    # Act
    runner = DatabricksConnectRunner(
        host=host,
        cluster_id="0000-000000-fakeclus",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
    )

    # Assert
    actual = runner.host
    expected = "https://fake-workspace.cloud.databricks.com"
    assert actual == expected


@pytest.mark.parametrize("value", [None, ""])
@pytest.mark.parametrize("field", ["host", "cluster_id", "client_id", "client_secret"])
def test_connect_runner_should_raise_required_argument_error_when_argument_is_missing(
    field: str, value: str | None
):
    # Arrange
    arguments = {
        "host": "https://fake-workspace.cloud.databricks.com",
        "cluster_id": "0000-000000-fakeclus",
        "client_id": "fake-client-id",
        "client_secret": "fake-client-secret",
    }
    arguments[field] = value

    # Act & Assert
    with pytest.raises(RequiredArgumentError, match=field):
        DatabricksConnectRunner(**arguments)


# ============================================================================
# Testing DatabricksConnectRunner setup
# ============================================================================
@patch("tiozin.api.tiozin.current_context")
@patch("tia_databricks.runners.connect_runner.DatabricksSession")
@patch("tia_databricks.runners.connect_runner.Config")
def test_setup_should_build_sdk_config_with_credentials(
    config_cls: MagicMock, _databricks_session: MagicMock, _current_context: MagicMock
):
    # Act
    runner = DatabricksConnectRunner(
        host="https://fake-workspace.cloud.databricks.com/",
        cluster_id="0000-000000-fakeclus",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
    )
    with runner():
        pass

    # Assert
    config_cls.assert_called_once_with(
        host="https://fake-workspace.cloud.databricks.com",
        cluster_id="0000-000000-fakeclus",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
    )


@patch("tiozin.api.tiozin.current_context")
@patch("tia_databricks.runners.connect_runner.DatabricksSession")
@patch("tia_databricks.runners.connect_runner.Config")
def test_setup_should_build_databricks_session_from_sdk_config(
    config_cls: MagicMock, databricks_session: MagicMock, _current_context: MagicMock
):
    # Arrange
    sdk_config = config_cls.return_value

    # Act
    runner = DatabricksConnectRunner(
        host="https://fake-workspace.cloud.databricks.com",
        cluster_id="0000-000000-fakeclus",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
    )
    with runner():
        pass

    # Assert
    databricks_session.builder.sdkConfig.assert_called_once_with(sdk_config)


@patch("tiozin.api.tiozin.current_context")
@patch("tia_databricks.runners.connect_runner.DatabricksSession")
@patch("tia_databricks.runners.connect_runner.Config")
def test_setup_should_expose_databricks_session(
    _config_cls: MagicMock, databricks_session: MagicMock, _current_context: MagicMock
):
    # Arrange
    session = databricks_session.builder.sdkConfig.return_value.getOrCreate.return_value

    # Act
    runner = DatabricksConnectRunner(
        host="https://fake-workspace.cloud.databricks.com",
        cluster_id="0000-000000-fakeclus",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
    )
    with runner() as active_runner:
        result = active_runner.session

    # Assert
    assert result is session


@patch("tiozin.api.tiozin.current_context")
@patch("tia_databricks.runners.connect_runner.DatabricksSession")
@patch("tia_databricks.runners.connect_runner.Config")
def test_setup_should_set_session_timezone(
    _config_cls: MagicMock, databricks_session: MagicMock, _current_context: MagicMock
):
    # Arrange
    session = databricks_session.builder.sdkConfig.return_value.getOrCreate.return_value

    # Act
    runner = DatabricksConnectRunner(
        host="https://fake-workspace.cloud.databricks.com",
        cluster_id="0000-000000-fakeclus",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
    )
    with runner():
        pass

    # Assert
    actual = session.conf.set.call_args_list
    expected = [
        call("spark.sql.session.timeZone", "UTC"),
    ]
    assert actual == expected


@patch("tiozin.api.tiozin.current_context")
@patch("tia_databricks.runners.connect_runner.DatabricksSession")
@patch("tia_databricks.runners.connect_runner.Config")
def test_setup_should_set_options_as_spark_conf(
    _config_cls: MagicMock, databricks_session: MagicMock, _current_context: MagicMock
):
    # Arrange
    session = databricks_session.builder.sdkConfig.return_value.getOrCreate.return_value
    options = {
        "spark.sql.shuffle.partitions": "200",
        "spark.sql.ansi.enabled": "true",
    }

    # Act
    runner = DatabricksConnectRunner(
        host="https://fake-workspace.cloud.databricks.com",
        cluster_id="0000-000000-fakeclus",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
        **options,
    )
    with runner():
        pass

    # Assert
    actual = session.conf.set.call_args_list
    expected = [
        call("spark.sql.session.timeZone", "UTC"),
        call("spark.sql.shuffle.partitions", "200"),
        call("spark.sql.ansi.enabled", "true"),
    ]
    assert actual == expected


@patch("tiozin.api.tiozin.current_context")
@patch("tia_databricks.runners.connect_runner.DatabricksSession")
@patch("tia_databricks.runners.connect_runner.Config")
def test_setup_should_reuse_session_when_session_already_exists(
    _config_cls: MagicMock, databricks_session: MagicMock, _current_context: MagicMock
):
    # Arrange
    builder = databricks_session.builder.sdkConfig.return_value

    # Act
    runner = DatabricksConnectRunner(
        host="https://fake-workspace.cloud.databricks.com",
        cluster_id="0000-000000-fakeclus",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
    )
    with runner():
        with runner():
            pass

    # Assert
    builder.getOrCreate.assert_called_once()
