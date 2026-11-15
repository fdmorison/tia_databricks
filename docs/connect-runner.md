# DatabricksConnectRunner

Runs Tiozin jobs inside a Databricks cluster through [Databricks Connect](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/). The job is planned locally and executed by the cluster, so steps read and write [Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/) tables from inside Databricks, with the access and features of the cluster.

The runner extends [SparkRunner](https://github.com/fdmorison/tiozin/blob/main/docs/tio_spark/runner.md). During setup, it connects to the cluster and opens a Spark session there. During teardown, it stops that session.

```yaml
runner:
  kind: DatabricksConnectRunner
  host: "{{ ENV.DATABRICKS_HOST }}"
  cluster_id: "{{ ENV.DATABRICKS_CLUSTER_ID }}"
  client_id: "{{ ENV.DATABRICKS_CLIENT_ID }}"
  client_secret: "{{ ENV.DATABRICKS_CLIENT_SECRET }}"
```

The `{{ ENV.NAME }}` syntax reads environment variables at runtime. See [Templates](https://github.com/fdmorison/tiozin/blob/main/docs/templates.md) for details.

## Parameters

| Property | Required | Default | Description |
| -------- | -------- | ------- | ----------- |
| `host` | Yes | | Databricks workspace URL, such as `https://my-workspace.cloud.databricks.com`. A trailing slash is ignored |
| `cluster_id` | Yes | | ID of the Databricks cluster that executes the job |
| `client_id` | Yes | | Client ID of the service principal |
| `client_secret` | Yes | | Client secret of the service principal |
| `**options` | No | | Spark configuration options applied to the session after it connects |

If any required parameter is missing or empty, creating the runner fails with a `RequiredArgumentError`.

## Creating the Runner in Python

The runner is exported from the `families.tia_databricks` package:

```python
from families.tia_databricks import DatabricksConnectRunner

runner = DatabricksConnectRunner(
    host="https://my-workspace.cloud.databricks.com",
    cluster_id="0123-456789-abcdefgh",
    client_id="my-client-id",
    client_secret="my-client-secret",
)
```

## Before Running a Job

The runner needs Databricks Connect installed and a cluster it can reach and attach to:

- `tia_databricks` must be installed with the `connect` extra.
- The cluster must be running, or be able to start.
- The service principal must be allowed to attach to the cluster.
- The installed `databricks-connect` version must match the cluster's Databricks Runtime version.

## Authentication

The runner signs in as a [service principal](https://docs.databricks.com/aws/en/admin/users-groups/service-principals) using the [OAuth machine-to-machine (M2M)](https://docs.databricks.com/aws/en/dev-tools/auth/oauth-m2m) client credentials flow. `client_id` and `client_secret` are that service principal's credentials.

Databricks Connect requests and refreshes the access token itself, so long-running jobs keep a valid token.

## Matching the Databricks Connect Version

The `connect` extra accepts `databricks-connect` versions from 15.4 up to, but not including, 17.0. Within that range, pin the release that matches the cluster's Databricks Runtime. For a cluster on Databricks Runtime 15.4:

```bash
pip install "tia_databricks[connect]" "databricks-connect==15.4.*"
```

## Passing Spark Config Options

Extra keys in the runner block are set on the session as [Spark configuration](https://spark.apache.org/docs/latest/configuration.html) options once it connects to the cluster.

```yaml
runner:
  kind: DatabricksConnectRunner
  host: "{{ ENV.DATABRICKS_HOST }}"
  cluster_id: "{{ ENV.DATABRICKS_CLUSTER_ID }}"
  client_id: "{{ ENV.DATABRICKS_CLIENT_ID }}"
  client_secret: "{{ ENV.DATABRICKS_CLIENT_SECRET }}"
  spark.sql.shuffle.partitions: 200
```

The runner sets `spark.sql.session.timeZone` to UTC before applying these options. An option with that key replaces the UTC setting.

## Related

- [tia_databricks family](index.md)
- [SparkRunner](https://github.com/fdmorison/tiozin/blob/main/docs/tio_spark/runner.md)
- [tio_spark family](https://github.com/fdmorison/tiozin/blob/main/docs/tio_spark/index.md)
- [Runners](https://github.com/fdmorison/tiozin/blob/main/docs/concepts/runners.md)
- [Databricks Connect](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/)
