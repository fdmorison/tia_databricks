from datetime import UTC, datetime
from unittest.mock import MagicMock, call, patch

import pytest
from databricks.sdk.errors import AlreadyExists, ResourceAlreadyExists
from databricks.sdk.service.catalog import (
    CreateRequestExternalLineage,
    ExternalLineageExternalMetadata,
    ExternalLineageObject,
    ExternalLineagePath,
    ExternalLineageTable,
    ExternalMetadata,
    SystemType,
)
from tiozin import LineageDataset, LineageRunEvent, Schema
from tiozin.api.metadata.lineage.enums import ProcessingType
from tiozin.api.metadata.lineage.model import LineageJob
from tiozin.api.metadata.schema.model import Property
from tiozin.exceptions import TiozinNotImplementedError

from tia_databricks import DatabricksLineageRegistry


# ============================================================================
# Testing DatabricksLineageRegistry setup and teardown
# ============================================================================
@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_setup_should_configure_workspace_connection(
    _workspace_client: MagicMock, config: MagicMock
):
    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
        timeout=30,
    )
    registry.setup()

    # Assert
    actual = config.call_args
    expected = call(
        host="https://fake-workspace.cloud.databricks.com",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
        http_timeout_seconds=30,
        retry_timeout_seconds=30,
    )
    assert actual == expected


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_setup_should_create_workspace_client(workspace_client: MagicMock, config: MagicMock):
    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
    )
    registry.setup()

    # Assert
    actual = workspace_client.call_args
    expected = call(config=config.return_value)
    assert actual == expected


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_setup_should_trim_connection_parameters(_workspace_client: MagicMock, config: MagicMock):
    # Act
    registry = DatabricksLineageRegistry(
        location="  https://fake-workspace.cloud.databricks.com  ",
        client_id="  fake-client-id  ",
        client_secret="  fake-client-secret  ",
        timeout=30,
    )
    registry.setup()

    # Assert
    actual = config.call_args
    expected = call(
        host="https://fake-workspace.cloud.databricks.com",
        client_id="fake-client-id",
        client_secret="fake-client-secret",
        http_timeout_seconds=30,
        retry_timeout_seconds=30,
    )
    assert actual == expected


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_setup_should_mark_registry_as_ready(_workspace_client: MagicMock, _config: MagicMock):
    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    )
    registry.setup()

    # Assert
    assert registry.ready


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_teardown_should_mark_registry_as_not_ready(
    _workspace_client: MagicMock, _config: MagicMock
):
    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    )
    registry.setup()
    registry.teardown()

    # Assert
    assert not registry.ready


# ============================================================================
# Testing DatabricksLineageRegistry.emit
# ============================================================================
@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_create_job_as_external_metadata(
    workspace_client: MagicMock, _config: MagicMock
):
    # Arrange
    client = workspace_client.return_value
    event = LineageRunEvent(
        type=LineageRunEvent.COMPLETE,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={"org": "acme", "layer": "raw"},
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    actual = client.external_metadata.create_external_metadata.call_args_list
    expected = [
        call(
            ExternalMetadata(
                name="acme_latam_ecommerce_checkout:sales_job",
                system_type=SystemType.OTHER,
                entity_type="job",
                properties={
                    "namespace": "acme.latam.ecommerce.checkout",
                    "name": "sales_job",
                    "org": "acme",
                    "layer": "raw",
                },
            )
        )
    ]
    assert actual == expected


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_create_step_as_external_metadata(
    workspace_client: MagicMock, _config: MagicMock
):
    # Arrange
    client = workspace_client.return_value
    event = LineageRunEvent(
        type=LineageRunEvent.COMPLETE,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job.load_customers",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={},
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    actual = client.external_metadata.create_external_metadata.call_args_list
    expected = [
        call(
            ExternalMetadata(
                name="acme_latam_ecommerce_checkout:sales_job_load_customers",
                system_type=SystemType.OTHER,
                entity_type="job",
                properties={
                    "namespace": "acme.latam.ecommerce.checkout",
                    "name": "sales_job.load_customers",
                },
            )
        )
    ]
    assert actual == expected


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_link_catalog_table_input_to_job(
    workspace_client: MagicMock, _config: MagicMock
):
    # Arrange
    client = workspace_client.return_value
    client.tables.exists.return_value.table_exists = True
    event = LineageRunEvent(
        type=LineageRunEvent.COMPLETE,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={},
        inputs=[LineageDataset(namespace="main", name="raw.customers")],
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    actual = client.external_lineage.create_external_lineage_relationship.call_args_list
    expected = [
        call(
            CreateRequestExternalLineage(
                source=ExternalLineageObject(
                    table=ExternalLineageTable(name="main.raw.customers"),
                ),
                target=ExternalLineageObject(
                    external_metadata=ExternalLineageExternalMetadata(
                        name="acme_latam_ecommerce_checkout:sales_job",
                    ),
                ),
            )
        )
    ]
    assert actual == expected


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_link_job_to_catalog_table_output(
    workspace_client: MagicMock, _config: MagicMock
):
    # Arrange
    client = workspace_client.return_value
    client.tables.exists.return_value.table_exists = True
    event = LineageRunEvent(
        type=LineageRunEvent.COMPLETE,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={},
        outputs=[LineageDataset(namespace="main", name="raw.customers")],
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    actual = client.external_lineage.create_external_lineage_relationship.call_args_list
    expected = [
        call(
            CreateRequestExternalLineage(
                source=ExternalLineageObject(
                    external_metadata=ExternalLineageExternalMetadata(
                        name="acme_latam_ecommerce_checkout:sales_job",
                    ),
                ),
                target=ExternalLineageObject(
                    table=ExternalLineageTable(name="main.raw.customers"),
                ),
            )
        )
    ]
    assert actual == expected


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_look_up_catalog_table_in_unity_catalog(
    workspace_client: MagicMock, _config: MagicMock
):
    # Arrange
    client = workspace_client.return_value
    client.tables.exists.return_value.table_exists = True
    event = LineageRunEvent(
        type=LineageRunEvent.COMPLETE,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={},
        inputs=[LineageDataset(namespace="main", name="raw.customers")],
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    actual = client.tables.exists.call_args_list
    expected = [call("main.raw.customers")]
    assert actual == expected


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_create_missing_catalog_table_as_external_metadata(
    workspace_client: MagicMock,
    _config: MagicMock,
):
    # Arrange
    client = workspace_client.return_value
    client.tables.exists.return_value.table_exists = False
    event = LineageRunEvent(
        type=LineageRunEvent.COMPLETE,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={},
        inputs=[LineageDataset(namespace="main", name="raw.customers")],
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    actual = client.external_metadata.create_external_metadata.call_args_list[1]
    expected = call(
        ExternalMetadata(
            name="main:raw_customers",
            system_type=SystemType.OTHER,
            entity_type="dataset",
            url="main:raw.customers",
            columns=None,
            properties={
                "namespace": "main",
                "name": "raw.customers",
            },
        )
    )
    assert actual == expected


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_link_missing_catalog_table_to_job(
    workspace_client: MagicMock, _config: MagicMock
):
    # Arrange
    client = workspace_client.return_value
    client.tables.exists.return_value.table_exists = False
    event = LineageRunEvent(
        type=LineageRunEvent.COMPLETE,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={},
        inputs=[LineageDataset(namespace="main", name="raw.customers")],
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    actual = client.external_lineage.create_external_lineage_relationship.call_args_list
    expected = [
        call(
            CreateRequestExternalLineage(
                source=ExternalLineageObject(
                    external_metadata=ExternalLineageExternalMetadata(
                        name="main:raw_customers",
                    ),
                ),
                target=ExternalLineageObject(
                    external_metadata=ExternalLineageExternalMetadata(
                        name="acme_latam_ecommerce_checkout:sales_job",
                    ),
                ),
            )
        )
    ]
    assert actual == expected


@pytest.mark.parametrize(
    "namespace, expected_url",
    [
        ("s3://bucket", "s3://bucket/data/customers"),
        (
            "abfss://container@account.dfs.core.windows.net",
            "abfss://container@account.dfs.core.windows.net/data/customers",
        ),
        ("gs://bucket", "gs://bucket/data/customers"),
    ],
)
@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_link_cloud_storage_dataset_as_path(
    workspace_client: MagicMock, _config: MagicMock, namespace: str, expected_url: str
):
    # Arrange
    client = workspace_client.return_value
    event = LineageRunEvent(
        type=LineageRunEvent.COMPLETE,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={},
        inputs=[LineageDataset(namespace=namespace, name="data/customers")],
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    actual = client.external_lineage.create_external_lineage_relationship.call_args_list
    expected = [
        call(
            CreateRequestExternalLineage(
                source=ExternalLineageObject(
                    path=ExternalLineagePath(url=expected_url),
                ),
                target=ExternalLineageObject(
                    external_metadata=ExternalLineageExternalMetadata(
                        name="acme_latam_ecommerce_checkout:sales_job",
                    ),
                ),
            )
        )
    ]
    assert actual == expected


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_link_storage_dataset_without_authority_as_path(
    workspace_client: MagicMock, _config: MagicMock
):
    # Arrange
    client = workspace_client.return_value
    event = LineageRunEvent(
        type=LineageRunEvent.COMPLETE,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={},
        inputs=[LineageDataset(namespace="dbfs", name="mnt/raw/customers.parquet")],
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    actual = client.external_lineage.create_external_lineage_relationship.call_args_list
    expected = [
        call(
            CreateRequestExternalLineage(
                source=ExternalLineageObject(
                    path=ExternalLineagePath(url="dbfs:/mnt/raw/customers.parquet"),
                ),
                target=ExternalLineageObject(
                    external_metadata=ExternalLineageExternalMetadata(
                        name="acme_latam_ecommerce_checkout:sales_job",
                    ),
                ),
            )
        )
    ]
    assert actual == expected


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_create_kafka_dataset_as_external_metadata(
    workspace_client: MagicMock, _config: MagicMock
):
    # Arrange
    client = workspace_client.return_value
    event = LineageRunEvent(
        type=LineageRunEvent.COMPLETE,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={},
        inputs=[LineageDataset(namespace="kafka://broker:9092", name="orders")],
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    actual = client.external_metadata.create_external_metadata.call_args_list[1]
    expected = call(
        ExternalMetadata(
            name="kafka_broker_9092:orders",
            system_type=SystemType.KAFKA,
            entity_type="dataset",
            url="kafka://broker:9092/orders",
            columns=None,
            properties={
                "namespace": "kafka://broker:9092",
                "name": "orders",
            },
        )
    )
    assert actual == expected


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_link_kafka_dataset_to_job(workspace_client: MagicMock, _config: MagicMock):
    # Arrange
    client = workspace_client.return_value
    event = LineageRunEvent(
        type=LineageRunEvent.COMPLETE,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={},
        inputs=[LineageDataset(namespace="kafka://broker:9092", name="orders")],
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    actual = client.external_lineage.create_external_lineage_relationship.call_args_list
    expected = [
        call(
            CreateRequestExternalLineage(
                source=ExternalLineageObject(
                    external_metadata=ExternalLineageExternalMetadata(
                        name="kafka_broker_9092:orders",
                    ),
                ),
                target=ExternalLineageObject(
                    external_metadata=ExternalLineageExternalMetadata(
                        name="acme_latam_ecommerce_checkout:sales_job",
                    ),
                ),
            )
        )
    ]
    assert actual == expected


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_not_look_up_kafka_dataset_in_unity_catalog(
    workspace_client: MagicMock, _config: MagicMock
):
    # Arrange
    client = workspace_client.return_value
    event = LineageRunEvent(
        type=LineageRunEvent.COMPLETE,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={},
        inputs=[LineageDataset(namespace="kafka://broker:9092", name="orders")],
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    client.tables.exists.assert_not_called()


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_list_schema_columns_of_external_dataset(
    workspace_client: MagicMock, _config: MagicMock
):
    # Arrange
    client = workspace_client.return_value
    event = LineageRunEvent(
        type=LineageRunEvent.COMPLETE,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={},
        inputs=[
            LineageDataset(
                namespace="kafka://broker:9092",
                name="orders",
                schema=Schema(
                    properties=[
                        Property(name="order_id", logicalType="integer"),
                        Property(name="status", logicalType="string"),
                    ]
                ),
            )
        ],
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    actual = client.external_metadata.create_external_metadata.call_args_list[1]
    expected = call(
        ExternalMetadata(
            name="kafka_broker_9092:orders",
            system_type=SystemType.KAFKA,
            entity_type="dataset",
            url="kafka://broker:9092/orders",
            columns=["order_id", "status"],
            properties={
                "namespace": "kafka://broker:9092",
                "name": "orders",
            },
        )
    )
    assert actual == expected


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_create_missing_local_file_as_external_metadata(
    workspace_client: MagicMock, _config: MagicMock
):
    # Arrange
    client = workspace_client.return_value
    client.tables.exists.return_value.table_exists = False
    event = LineageRunEvent(
        type=LineageRunEvent.COMPLETE,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={},
        inputs=[LineageDataset(namespace="file", name="raw.customers")],
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    actual = client.external_metadata.create_external_metadata.call_args_list[1]
    expected = call(
        ExternalMetadata(
            name="file:raw_customers",
            system_type=SystemType.OTHER,
            entity_type="dataset",
            url="file:raw.customers",
            columns=None,
            properties={
                "namespace": "file",
                "name": "raw.customers",
            },
        )
    )
    assert actual == expected


@pytest.mark.parametrize(
    "type",
    [LineageRunEvent.START, LineageRunEvent.FAIL, LineageRunEvent.ABORT],
)
@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_not_call_api_when_run_is_not_complete(
    workspace_client: MagicMock, _config: MagicMock, type: str
):
    # Arrange
    client = workspace_client.return_value
    event = LineageRunEvent(
        type=type,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={},
        inputs=[LineageDataset(namespace="main", name="raw.customers")],
        outputs=[LineageDataset(namespace="main", name="refined.customers")],
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    actual = client.method_calls
    expected = []
    assert actual == expected


@pytest.mark.parametrize("error", [AlreadyExists, ResourceAlreadyExists])
@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_ignore_existing_external_metadata(
    workspace_client: MagicMock, _config: MagicMock, error: type[Exception]
):
    # Arrange
    client = workspace_client.return_value
    client.external_metadata.create_external_metadata.side_effect = error("already exists")
    event = LineageRunEvent(
        type=LineageRunEvent.COMPLETE,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={},
        inputs=[LineageDataset(namespace="kafka://broker:9092", name="orders")],
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    actual = client.external_lineage.create_external_lineage_relationship.call_args_list
    expected = [
        call(
            CreateRequestExternalLineage(
                source=ExternalLineageObject(
                    external_metadata=ExternalLineageExternalMetadata(
                        name="kafka_broker_9092:orders",
                    ),
                ),
                target=ExternalLineageObject(
                    external_metadata=ExternalLineageExternalMetadata(
                        name="acme_latam_ecommerce_checkout:sales_job",
                    ),
                ),
            )
        )
    ]
    assert actual == expected


@pytest.mark.parametrize("error", [AlreadyExists, ResourceAlreadyExists])
@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_ignore_existing_relationship(
    workspace_client: MagicMock, _config: MagicMock, error: type[Exception]
):
    # Arrange
    client = workspace_client.return_value
    client.external_lineage.create_external_lineage_relationship.side_effect = error(
        "already exists"
    )
    event = LineageRunEvent(
        type=LineageRunEvent.COMPLETE,
        producer="tiozin/test",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        nominal_time=datetime(2024, 1, 1, tzinfo=UTC),
        run_id="fake-run-id",
        job=LineageJob(
            namespace="acme.latam.ecommerce.checkout",
            name="sales_job",
            type=LineageJob.JOB,
            processing_type=ProcessingType.BATCH,
            integration="TIOZIN",
        ),
        tags={},
        inputs=[LineageDataset(namespace="main", name="raw.customers")],
        outputs=[LineageDataset(namespace="main", name="refined.customers")],
    )

    # Act
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    registry.emit(event)

    # Assert
    actual = client.external_lineage.create_external_lineage_relationship.call_count
    expected = 2
    assert actual == expected


@patch("tia_databricks.registries.lineage_registry.Config")
@patch("tia_databricks.registries.lineage_registry.WorkspaceClient")
def test_emit_should_raise_not_implemented_error_when_event_is_not_run_event(
    _workspace_client: MagicMock,
    _config: MagicMock,
):
    # Arrange
    event = LineageDataset(namespace="main", name="raw.customers")

    # Act & Assert
    registry = DatabricksLineageRegistry(
        location="https://fake-workspace.cloud.databricks.com",
    ).__wrapped__.__wrapped__
    registry.setup()
    with pytest.raises(TiozinNotImplementedError, match="LineageDataset"):
        registry.emit(event)
