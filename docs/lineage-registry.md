# DatabricksLineageRegistry

Reports the lineage of Tiozin jobs to [Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/), so the catalog shows which datasets each job reads and writes.

Unity Catalog does not accept [OpenLineage](https://openlineage.io/) events. The registry reports through the Unity Catalog [External Lineage API](https://docs.databricks.com/aws/en/data-governance/unity-catalog/external-lineage) instead, which stores lineage as relationships between objects.

```yaml
registries:
  lineage:
    kind: DatabricksLineageRegistry
    location: "{{ ENV.DATABRICKS_HOST }}"
    client_id: "{{ ENV.DATABRICKS_CLIENT_ID }}"
    client_secret: "{{ ENV.DATABRICKS_CLIENT_SECRET }}"
    emit_level: job
```

Add the block to the `tiozin.yaml` file, as described in [Registries](https://github.com/fdmorison/tiozin/blob/main/docs/settings/index.md#registries). `{{ ENV.NAME }}` reads an environment variable at runtime. See [Templates](https://github.com/fdmorison/tiozin/blob/main/docs/templates.md).

## Parameters

| Property | Required | Default | Description |
| -------- | -------- | ------- | ----------- |
| `location` | No | | Databricks workspace URL, such as `https://my-workspace.cloud.databricks.com`. When not set, the Databricks SDK takes it from `DATABRICKS_HOST` or from the notebook context |
| `client_id` | No | | Client ID of the service principal. When not set, the Databricks SDK uses its default authentication |
| `client_secret` | No | | Client secret of the service principal |
| `emit_level` | No | `job` | What gets reported: `job` for the job, `step` for each step, or `all` for both |
| `timeout` | No | `3` | Time limit in seconds for each request to the workspace, and for all retries of a failed request together |
| `**options` | No | | Additional arguments accepted by every lineage registry. See [Registries](https://github.com/fdmorison/tiozin/blob/main/docs/concepts/registries.md) |

## Creating the Registry in Python

```python
from tia_databricks import DatabricksLineageRegistry

registry = DatabricksLineageRegistry(
    location="https://my-workspace.cloud.databricks.com",
    client_id="my-client-id",
    client_secret="my-client-secret",
)
```

## Before Running a Job

The identity the registry signs in with needs these privileges in Unity Catalog:

- `CREATE EXTERNAL METADATA` on the metastore.
- `SELECT` on the Unity Catalog tables the job reads.
- `MODIFY` on the Unity Catalog tables the job writes.
- Permission to see each table the registry links, such as `BROWSE` on its catalog or schema. `SELECT` already covers the tables the job reads.

See the [Databricks documentation on external lineage](https://docs.databricks.com/aws/en/data-governance/unity-catalog/external-lineage) for how to grant them.

## How Jobs Appear in Unity Catalog

Each reported job becomes an external metadata object linked to its inputs and outputs, so the lineage reads `input -> job -> output`. The object is named after the job namespace and name, in snake_case, joined by `:`. For the [one-minute example](../examples/jobs/oneminute.yaml), with the default namespace `org.region.domain.subdomain`:

```yaml
org: tiozin
region: latam
domain: literature
subdomain: classics
name: ingestion_hamlet_job
# → tiozin_latam_literature_classics:ingestion_hamlet_job
```

The object also keeps the job namespace and name as properties, along with the job's taxonomy and ownership fields, such as `org`, `layer`, `owner` and `cost_center`, and its labels.

With `emit_level: step` or `emit_level: all`, each step gets its own object, linked to the datasets that step reports. The `save_hamlet` step of the same job becomes `tiozin_latam_literature_classics:ingestion_hamlet_job:save_hamlet`.

## How Datasets Map to Unity Catalog

- A Unity Catalog table, reported as `catalog.schema.table`, links to that table when it exists in Unity Catalog, and otherwise becomes an external metadata object.
- A file in cloud storage (`s3`, `s3a`, `s3n`, `gs`, `abfs`, `abfss`, `wasb`, `wasbs` or `dbfs`) links to its path.
- Any other dataset, such as a Kafka topic, a Postgres table or a local file, becomes an external metadata object, named after the dataset namespace and name the same way as a job object.

| Dataset | In Unity Catalog |
| ------- | ---------------- |
| `tiozin.default.raw_shakespeare_hamlet` | Table `tiozin.default.raw_shakespeare_hamlet` |
| Table `raw.customers` on `main`, missing from Unity Catalog | External metadata object `main:raw_customers` |
| `s3://my-bucket/raw/orders` | Path `s3://my-bucket/raw/orders` |
| `dbfs:/mnt/raw/orders` | Path `dbfs:/mnt/raw/orders` |
| Topic `orders` on `kafka://broker:9092` | External metadata object `kafka_broker_9092:orders` |
| Local file `examples/data/shakespeare/hamlet.txt` | External metadata object `file:examples_data_shakespeare_hamlet_txt` |

Each of these objects keeps the dataset namespace and name as properties. An external metadata object also links to the original dataset, shown in the lineage graph as `kafka://broker:9092/orders` for the Kafka topic and `file:examples/data/shakespeare/hamlet.txt` for the local file. When the dataset carries a schema, the object also lists its top-level columns.

## System Types

Every external metadata object has a system type. For a dataset, it comes from the scheme of its namespace:

| Scheme | System type |
| ------ | ----------- |
| `kafka` | `KAFKA` |
| `postgres`, `postgresql` | `POSTGRESQL` |
| `mysql` | `MYSQL` |
| `mssql`, `sqlserver` | `MICROSOFT_SQL_SERVER` |
| `oracle` | `ORACLE` |
| `teradata` | `TERADATA` |
| `snowflake` | `SNOWFLAKE` |
| `bigquery` | `GOOGLE_BIGQUERY` |
| `redshift` | `AMAZON_REDSHIFT` |
| `mongodb` | `MONGODB` |

Any other scheme, local files included, gets the `OTHER` system type. Job and step objects are `OTHER` too.

## When Lineage Is Reported

The registry reports a run once it completes. Started, failed and aborted runs leave Unity Catalog as it is.

Running the same job again leaves existing objects and relationships as they are and does not fail.

If reporting fails, for example because a privilege is missing, Tiozin logs a warning and the job goes on.

## Authentication

With `client_id` and `client_secret`, the registry signs in as a [service principal](https://docs.databricks.com/aws/en/admin/users-groups/service-principals) using the [OAuth machine-to-machine (M2M)](https://docs.databricks.com/aws/en/dev-tools/auth/oauth-m2m) flow.

Without them, the registry relies on the [Databricks SDK default authentication](https://docs.databricks.com/aws/en/dev-tools/auth/unified-auth). Inside a Databricks notebook, or with the workspace URL and credentials already set up for the SDK, the registry block can be as short as this:

```yaml
registries:
  lineage:
    kind: DatabricksLineageRegistry
```

## When Lineage Is Missing

Without the `CREATE EXTERNAL METADATA` privilege, lineage never reaches Unity Catalog and the job logs show a warning like this one:

```text
[warning] Lineage emission failed: Principal '<principal>' does not have CREATE EXTERNAL METADATA on Metastore '<metastore>'.
```

A metastore admin or an account admin can grant it with SQL:

```sql
GRANT CREATE EXTERNAL METADATA ON METASTORE TO `<application-id>`;
```

For a service principal, the principal is its application ID.

The same grant works from Catalog Explorer:

1. Click **Catalog**.
2. Click the gear icon at the top of the Catalog pane and select **Metastore**.
3. Open the **Permissions** tab and click **Grant**.
4. Choose the principal and the `CREATE EXTERNAL METADATA` privilege.

See [Grant permissions on a metastore](https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/).

## Related

- [tia_databricks family](index.md)
- [DatabricksConnectRunner](connect-runner.md)
- [DatabricksExternalRunner](external-runner.md)
- [Registries](https://github.com/fdmorison/tiozin/blob/main/docs/concepts/registries.md)
- [External lineage in Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/external-lineage)
- [Manage privileges in Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/)
