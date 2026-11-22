import re
from contextlib import suppress

from databricks.sdk import WorkspaceClient
from databricks.sdk.config import Config
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
from tiozin import LineageDataset, LineageEvent, LineageRegistry, LineageRunEvent
from tiozin.exceptions import TiozinNotImplementedError
from tiozin.utils import slugify, trim

SCHEME_SEPARATOR = "://"
JOB_ENTITY_TYPE = "job"
DATASET_ENTITY_TYPE = "dataset"
UC_TABLE_PATTERN = re.compile(r"^\w+\.\w+\.\w+$")
STORAGE_SCHEMES = {"s3", "s3a", "s3n", "gs", "abfs", "abfss", "wasb", "wasbs", "dbfs"}
SYSTEM_TYPES = {
    "kafka": SystemType.KAFKA,
    "postgres": SystemType.POSTGRESQL,
    "postgresql": SystemType.POSTGRESQL,
    "mysql": SystemType.MYSQL,
    "mssql": SystemType.MICROSOFT_SQL_SERVER,
    "sqlserver": SystemType.MICROSOFT_SQL_SERVER,
    "oracle": SystemType.ORACLE,
    "teradata": SystemType.TERADATA,
    "snowflake": SystemType.SNOWFLAKE,
    "bigquery": SystemType.GOOGLE_BIGQUERY,
    "redshift": SystemType.AMAZON_REDSHIFT,
    "mongodb": SystemType.MONGODB,
}


class DatabricksLineageRegistry(LineageRegistry):
    """
    Reports lineage to Databricks Unity Catalog.

    Unity Catalog does not accept OpenLineage events. This registry uses its
    External Lineage API instead, which stores lineage as relationships
    between objects.

    Each job or step becomes an external metadata object, and its datasets
    are linked to it as `input -> job -> output`. Datasets map to Unity
    Catalog objects as follows:

    - A catalog table (`catalog.schema.table`) that exists in Unity Catalog links to that table.
    - A cloud storage URI (`s3://`, `abfss://`, `gs://`, `dbfs:/`...) links to the path.
    - Any other dataset, such as a Kafka topic or a Postgres table, becomes an
      external metadata object whose system type comes from the namespace scheme.

    Only completed runs are reported. Relationships and objects that already
    exist are kept, so running a job again reports nothing new.

    The caller needs the `CREATE EXTERNAL METADATA` privilege on the metastore,
    `SELECT` on the Unity Catalog tables the job reads, `MODIFY` on the ones
    it writes, and permission to see each linked table, such as `BROWSE`.

    For details about the External Lineage API, refer to:

    https://docs.databricks.com/aws/en/data-governance/unity-catalog/external-lineage

    Attributes:
        location:
            Databricks workspace URL (e.g. `https://my-workspace.cloud.databricks.com`).
            When not set, the Databricks SDK resolves it from `DATABRICKS_HOST`
            or from the notebook context.

        client_id:
            Client ID of the service principal. When not set, the Databricks
            SDK uses its default authentication.

        client_secret:
            Client secret of the service principal.

        **options:
            Additional arguments accepted by `LineageRegistry`, such as
            `emit_level` and `timeout`.

    Examples:

        ```python
        DatabricksLineageRegistry(
            location="https://my-workspace.cloud.databricks.com",
            client_id="my-client-id",
            client_secret="my-client-secret",
        )
        ```

        ```yaml
        registries:
          lineage:
            kind: DatabricksLineageRegistry
            location: "{{ ENV.DATABRICKS_HOST }}"
            client_id: "{{ ENV.DATABRICKS_CLIENT_ID }}"
            client_secret: "{{ ENV.DATABRICKS_CLIENT_SECRET }}"
            emit_level: job
        ```
    """

    def __init__(
        self,
        location: str = None,
        client_id: str = None,
        client_secret: str = None,
        **options,
    ) -> None:
        super().__init__(location=trim(location), **options)
        self.client_id = trim(client_id)
        self.client_secret = trim(client_secret)
        self._client: WorkspaceClient = None

    def setup(self) -> None:
        self._client = WorkspaceClient(
            config=Config(
                host=self.location,
                client_id=self.client_id,
                client_secret=self.client_secret,
                http_timeout_seconds=self.timeout,
                retry_timeout_seconds=self.timeout,
            ),
        )
        self.ready = True

    def teardown(self) -> None:
        self._client = None
        self.ready = False

    def emit(self, event: LineageEvent) -> None:
        TiozinNotImplementedError.raise_if(
            not isinstance(event, LineageRunEvent),
            "DatabricksLineageRegistry only accepts LineageRunEvent, got `{type}`",
            type=type(event).__name__,
        )

        if event.type != LineageRunEvent.COMPLETE:
            return

        job = self._create_external_metadata(
            ExternalMetadata(
                name=":".join(
                    [slugify(event.job.namespace), *map(slugify, event.job.name.split("."))]
                ),
                system_type=SystemType.OTHER,
                entity_type=JOB_ENTITY_TYPE,
                properties={
                    "namespace": event.job.namespace,
                    "name": event.job.name,
                    **event.tags,
                },
            )
        )

        for dataset in event.inputs:
            self._create_relationship(source=self._as_dataset(dataset), target=job)

        for dataset in event.outputs:
            self._create_relationship(source=job, target=self._as_dataset(dataset))

    def _as_dataset(self, dataset: LineageDataset) -> ExternalLineageObject:
        namespace = dataset.namespace or ""
        scheme = namespace.split(SCHEME_SEPARATOR)[0]
        qualified_name = f"{namespace}.{dataset.name}"
        is_uri = SCHEME_SEPARATOR in namespace
        is_cloud_storage = scheme in STORAGE_SCHEMES

        if (
            UC_TABLE_PATTERN.match(qualified_name)
            and self._client.tables.exists(qualified_name).table_exists
        ):
            return ExternalLineageObject(table=ExternalLineageTable(name=qualified_name))

        if is_cloud_storage:
            url = f"{namespace}/{dataset.name}" if is_uri else f"{namespace}:/{dataset.name}"
            return ExternalLineageObject(path=ExternalLineagePath(url=url))

        return self._create_external_metadata(
            ExternalMetadata(
                name=f"{slugify(namespace)}:{slugify(dataset.name)}",
                system_type=SYSTEM_TYPES.get(scheme, SystemType.OTHER),
                entity_type=DATASET_ENTITY_TYPE,
                url=f"{namespace}/{dataset.name}" if is_uri else f"{namespace}:{dataset.name}",
                properties={
                    "namespace": dataset.namespace,
                    "name": dataset.name,
                },
                columns=[p.name for p in dataset.schema.properties or []]
                if dataset.schema
                else None,
            )
        )

    def _create_external_metadata(self, metadata: ExternalMetadata) -> ExternalLineageObject:
        with suppress(AlreadyExists, ResourceAlreadyExists):
            self._client.external_metadata.create_external_metadata(metadata)

        return ExternalLineageObject(
            external_metadata=ExternalLineageExternalMetadata(name=metadata.name),
        )

    def _create_relationship(
        self, source: ExternalLineageObject, target: ExternalLineageObject
    ) -> None:
        with suppress(AlreadyExists, ResourceAlreadyExists):
            self._client.external_lineage.create_external_lineage_relationship(
                CreateRequestExternalLineage(source=source, target=target)
            )
