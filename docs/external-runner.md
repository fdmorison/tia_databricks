# DatabricksExternalRunner

Runs Tiozin jobs on a local Spark session that reads and writes [Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/) tables from outside Databricks. Spark runs on the machine that runs the job.

The runner extends [SparkRunner](https://github.com/fdmorison/tio_spark/blob/main/docs/runner.md). During setup, it registers the catalog in the Spark session and opens the session. During teardown, it stops that session.

```yaml
runner:
  kind: DatabricksExternalRunner
  catalog: my_catalog
  host: "{{ ENV.DATABRICKS_HOST }}"
  client_id: "{{ ENV.DATABRICKS_CLIENT_ID }}"
  client_secret: "{{ ENV.DATABRICKS_CLIENT_SECRET }}"
  format: iceberg
```

The `{{ ENV.NAME }}` syntax reads environment variables at runtime. See [Templates](https://github.com/fdmorison/tiozin/blob/main/docs/templates.md) for details.

## Parameters

| Property | Required | Default | Description |
| -------- | -------- | ------- | ----------- |
| `catalog` | Yes | | Name of the Unity Catalog catalog to register in Spark. It becomes the default catalog of the session |
| `host` | Yes | | Databricks workspace URL, such as `https://my-workspace.cloud.databricks.com`. A trailing slash is ignored |
| `client_id` | Yes | | Client ID of the service principal |
| `client_secret` | Yes | | Client secret of the service principal |
| `scope` | No | `unity-catalog` | OAuth scope requested with the token |
| `format` | No | `delta` | Table format of the session, `delta` or `iceberg` |
| `**options` | No | | Additional arguments accepted by [SparkRunner](https://github.com/fdmorison/tio_spark/blob/main/docs/runner.md), including Spark configuration options |

If any required parameter is missing or empty, creating the runner fails with a `RequiredArgumentError`.

## Creating the Runner in Python

The runner is exported from the `tia_databricks` package:

```python
from tia_databricks import DatabricksExternalRunner

runner = DatabricksExternalRunner(
    catalog="my_catalog",
    host="https://my-workspace.cloud.databricks.com",
    client_id="my-client-id",
    client_secret="my-client-secret",
)
```

## Before Running a Job

The runner needs a local PySpark and a metastore that accepts access from outside Databricks:

- `tia_databricks` must be installed with the `tio_spark35` or `tio_spark40` extra, or alongside a separately installed PySpark. See [Installation](installation.md#running-spark-locally).
- The target metastore must have external access enabled.
- The service principal must hold the `EXTERNAL USE SCHEMA` grant on the target schema.

See the [Databricks documentation on external access to Unity Catalog](https://docs.databricks.com/aws/en/external-access/unity-rest) for both settings.

## Referring to Tables

The catalog named in `catalog` becomes the default catalog of the session. Steps can refer to tables as `schema.table` or `catalog.schema.table`.

With `catalog: tiozin`, an output can name its table either way:

```yaml
outputs:
  - kind: SparkTableOutput
    name: save_customers
    table: default.raw_storefront_customers
    # same table as tiozin.default.raw_storefront_customers
```

## Choosing the Table Format

A session works with one table format at a time, so pair the runner's `format` with outputs that write the same format. The runner defaults to `delta`, while [SparkTableOutput](https://github.com/fdmorison/tio_spark/blob/main/docs/table-output.md) defaults to `iceberg`. With the runner default, set `format: delta` on each output.

To write [Apache Iceberg](https://iceberg.apache.org/) tables, set `format: iceberg` on the runner. Spark then reaches Unity Catalog through its Iceberg REST catalog. See the [Databricks documentation on Iceberg clients](https://docs.databricks.com/aws/en/external-access/iceberg).

```yaml
runner:
  kind: DatabricksExternalRunner
  catalog: tiozin
  host: "{{ ENV.DATABRICKS_HOST }}"
  client_id: "{{ ENV.DATABRICKS_CLIENT_ID }}"
  client_secret: "{{ ENV.DATABRICKS_CLIENT_SECRET }}"
  format: iceberg

outputs:
  - kind: SparkTableOutput
    name: save_customers
    table: tiozin.default.raw_storefront_customers
    format: iceberg
    mode: merge
    merge_keys: id
```

## Authentication

The runner signs in as a [service principal](https://docs.databricks.com/aws/en/admin/users-groups/service-principals) using the [OAuth machine-to-machine (M2M)](https://docs.databricks.com/aws/en/dev-tools/auth/oauth-m2m) client credentials flow. `client_id` and `client_secret` are that service principal's credentials, and `scope` is the OAuth scope requested with the token.

The catalog client requests and refreshes the access token itself, so long-running jobs keep a valid token.

## Passing Spark Config Options

Extra keys in the runner block go to [SparkRunner](https://github.com/fdmorison/tio_spark/blob/main/docs/runner.md), which sets them on the session as [Spark configuration](https://spark.apache.org/docs/latest/configuration.html) options.

```yaml
runner:
  kind: DatabricksExternalRunner
  catalog: tiozin
  host: "{{ ENV.DATABRICKS_HOST }}"
  client_id: "{{ ENV.DATABRICKS_CLIENT_ID }}"
  client_secret: "{{ ENV.DATABRICKS_CLIENT_SECRET }}"
  spark.sql.shuffle.partitions: 200
```

## Related

- [tia_databricks family](index.md)
- [DatabricksConnectRunner](connect-runner.md)
- [SparkRunner](https://github.com/fdmorison/tio_spark/blob/main/docs/runner.md)
- [tio_spark family](https://github.com/fdmorison/tio_spark/blob/main/docs/index.md)
- [Runners](https://github.com/fdmorison/tiozin/blob/main/docs/concepts/runners.md)
- [Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/)
