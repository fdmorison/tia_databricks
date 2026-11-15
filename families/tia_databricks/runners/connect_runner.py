from databricks.connect import DatabricksSession
from databricks.sdk.core import Config
from tiozin import config
from tiozin.exceptions import RequiredArgumentError
from tiozin.family.tio_spark import SparkRunner
from tiozin.utils import trim


class DatabricksConnectRunner(SparkRunner):
    """
    Runs Spark jobs inside a Databricks cluster through Databricks Connect.

    The job is planned locally and executed by the cluster, so steps read and
    write Unity Catalog tables from inside Databricks, with the access and
    features of the cluster.

    Declare the workspace URL, the cluster ID and the service principal
    credentials. The cluster must be running, or be able to start, and the
    service principal must be allowed to attach to it.

    The runner authenticates as a service principal using the OAuth M-2M
    (client credentials) flow. Databricks Connect requests and refreshes the
    access token itself, so long-running jobs keep a valid token.

    The installed `databricks-connect` version must match the Databricks
    Runtime version of the cluster.

    For details about Databricks Connect, refer to:

    https://docs.databricks.com/aws/en/dev-tools/databricks-connect/

    Attributes:
        host:
            Databricks workspace URL (e.g. `https://my-workspace.cloud.databricks.com`).

        cluster_id:
            ID of the Databricks cluster that executes the job.

        client_id:
            Client ID of the service principal.

        client_secret:
            Client secret of the service principal.

        **options:
            Additional arguments accepted by `SparkRunner`, including Spark
            configuration options.

    Examples:

        ```python
        DatabricksConnectRunner(
            host="https://my-workspace.cloud.databricks.com",
            cluster_id="0123-456789-abcdefgh",
            client_id="my-client-id",
            client_secret="my-client-secret",
        )
        ```

        ```yaml
        runner:
          kind: DatabricksConnectRunner
          host: "{{ ENV.DATABRICKS_HOST }}"
          cluster_id: "{{ ENV.DATABRICKS_CLUSTER_ID }}"
          client_id: "{{ ENV.DATABRICKS_CLIENT_ID }}"
          client_secret: "{{ ENV.DATABRICKS_CLIENT_SECRET }}"
        ```
    """

    def __init__(
        self,
        host: str = None,
        cluster_id: str = None,
        client_id: str = None,
        client_secret: str = None,
        **options,
    ) -> None:
        super().__init__(**options)
        RequiredArgumentError.raise_if_missing(
            host=host,
            cluster_id=cluster_id,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.host = trim(host).rstrip("/")
        self.cluster_id = trim(cluster_id)
        self.client_id = trim(client_id)
        self.client_secret = trim(client_secret)

    def setup(self) -> None:
        if self._spark:
            return

        self.info(f"🔌 Connecting to the Databricks cluster {self.cluster_id}")

        sdk_config = Config(
            host=self.host,
            cluster_id=self.cluster_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        self._spark = DatabricksSession.builder.sdkConfig(sdk_config).getOrCreate()
        self._spark.conf.set("spark.sql.session.timeZone", str(config.app_timezone))

        for name, value in self.options.items():
            self._spark.conf.set(name, value)

        self.info(f"🔥 SparkSession ready for {self.context.name}")
