from tio_spark import SparkRunner
from tiozin.exceptions import RequiredArgumentError
from tiozin.utils import default, trim, trim_lower

from ..typehints import DatabricksTableFormat

DEFAULT_OAUTH_SCOPE = "unity-catalog"
DEFAULT_TABLE_FORMAT = "delta"
DELTA_SQL_EXTENSIONS = "io.delta.sql.DeltaSparkSessionExtension"
DELTA_SESSION_CATALOG = "org.apache.spark.sql.delta.catalog.DeltaCatalog"
UNITY_CATALOG_CLASS = "io.unitycatalog.spark.UCSingleCatalog"
S3A_FILESYSTEM_CLASS = "org.apache.hadoop.fs.s3a.S3AFileSystem"
ICEBERG_SQL_EXTENSIONS = "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
ICEBERG_CATALOG_CLASS = "org.apache.iceberg.spark.SparkCatalog"


class DatabricksExternalRunner(SparkRunner):
    """
    Runs Spark jobs that read and write Databricks Unity Catalog tables from
    outside Databricks.

    Declare the catalog, the workspace URL and the service principal
    credentials. The catalog becomes the default catalog of the session, so
    steps can refer to tables as `schema.table` or `catalog.schema.table`.

    Choose the table format of the session with `format`. A session works
    with one format at a time, so pair it with outputs that write the same
    format.

    The runner authenticates as a service principal using the OAuth M2M
    (client credentials) flow. The catalog client requests and refreshes the
    access token itself, so long-running jobs keep a valid token.

    The target metastore must have external access enabled and the service
    principal must hold the `EXTERNAL USE SCHEMA` grant on the target schema.

    For details about Unity Catalog integration with Spark, refer to:

    https://docs.databricks.com/aws/en/external-access/unity-rest
    https://docs.databricks.com/aws/en/external-access/iceberg

    Attributes:
        catalog:
            Name of the Unity Catalog catalog to register in Spark.

        host:
            Databricks workspace URL (e.g. `https://my-workspace.cloud.databricks.com`).

        client_id:
            Client ID of the service principal.

        client_secret:
            Client secret of the service principal.

        scope:
            OAuth scope requested with the token. Defaults to `unity-catalog`.

        format:
            Table format of the session, `delta` or `iceberg`. Defaults to `delta`.

        **options:
            Additional arguments accepted by `SparkRunner`, including Spark
            configuration options.

    Examples:

        ```python
        DatabricksExternalRunner(
            catalog="my_catalog",
            host="https://my-workspace.cloud.databricks.com",
            client_id="my-client-id",
            client_secret="my-client-secret",
        )
        ```

        ```yaml
        runner:
          kind: DatabricksExternalRunner
          catalog: my_catalog
          host: "{{ ENV.DATABRICKS_HOST }}"
          client_id: "{{ ENV.DATABRICKS_CLIENT_ID }}"
          client_secret: "{{ ENV.DATABRICKS_CLIENT_SECRET }}"
          format: iceberg
        ```
    """

    def __init__(
        self,
        catalog: str = None,
        host: str = None,
        client_id: str = None,
        client_secret: str = None,
        scope: str = None,
        format: DatabricksTableFormat = None,
        **options,
    ) -> None:
        super().__init__(**options)
        RequiredArgumentError.raise_if_missing(
            catalog=catalog,
            host=host,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.format = trim_lower(default(format, DEFAULT_TABLE_FORMAT))
        self.catalog = trim(catalog)
        self.host = trim(host).rstrip("/")
        self.token_url = f"{self.host}/oidc/v1/token"
        self.client_id = trim(client_id)
        self.client_secret = trim(client_secret)
        self.scope = trim(default(scope, DEFAULT_OAUTH_SCOPE))

    def setup(self) -> None:
        if self._spark:
            return

        self.info(f"Setting up Unity Catalog: {self.catalog}")

        catalog = f"spark.sql.catalog.{self.catalog}"

        match self.format:
            case "delta":
                # Tested with Spark 4.0.2, Delta 4.3.0 and unitycatalog-spark 0.6.0
                self.options["spark.sql.extensions"] = DELTA_SQL_EXTENSIONS
                self.options["spark.sql.catalog.spark_catalog"] = DELTA_SESSION_CATALOG
                self.options[catalog] = UNITY_CATALOG_CLASS
                self.options[f"{catalog}.uri"] = self.host
                self.options[f"{catalog}.auth.type"] = "oauth"
                self.options[f"{catalog}.auth.oauth.uri"] = self.token_url
                self.options[f"{catalog}.auth.oauth.clientId"] = self.client_id
                self.options[f"{catalog}.auth.oauth.clientSecret"] = self.client_secret
                self.options[f"{catalog}.auth.oauth.scope"] = self.scope
                self.options["spark.hadoop.fs.s3.impl"] = S3A_FILESYSTEM_CLASS
            case "iceberg":
                # Tested with Spark 3.5.4 and Iceberg 1.7.1
                self.options["spark.sql.extensions"] = ICEBERG_SQL_EXTENSIONS
                self.options[catalog] = ICEBERG_CATALOG_CLASS
                self.options[f"{catalog}.type"] = "rest"
                self.options[f"{catalog}.uri"] = f"{self.host}/api/2.1/unity-catalog/iceberg-rest"
                self.options[f"{catalog}.warehouse"] = self.catalog
                self.options[f"{catalog}.rest.auth.type"] = "oauth2"
                self.options[f"{catalog}.oauth2-server-uri"] = self.token_url
                self.options[f"{catalog}.credential"] = f"{self.client_id}:{self.client_secret}"
                self.options[f"{catalog}.scope"] = self.scope

        self.options["spark.sql.defaultCatalog"] = self.catalog

        super().setup()
