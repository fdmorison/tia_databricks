# Examples

All examples live under [`examples/jobs/`](../examples/jobs/) in the repository, and their source data lives under [`examples/data/`](../examples/data/). Each example is a self-contained job manifest that reads and writes tables in the `data_platform` catalog of [Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/).

The Ecommerce and Shakespeare scenarios mirror the [Spark examples in Tiozin](https://github.com/fdmorison/tiozin/blob/main/docs/examples.md), adapted to run against [Databricks](https://docs.databricks.com/).

## How the Folder Structure Works

Jobs are grouped by data product, and each job within a product gets its own YAML file named after its layer or purpose:

```text
examples/jobs/
  ecommerce/
    ingestion_customer_job.yaml
    ingestion_orders_job.yaml
    refined_orders_job.yaml
  shakespeare/
    ingestion_job.yaml
    refined_hamlet_job.yaml
    refined_kinglear_job.yaml
    refined_loverscomplaint_job.yaml
    refined_sonnets_job.yaml
```

One folder per data product. One YAML per job. No shared state between files.

## Two Kinds of Jobs

Each scenario has ingestion jobs and refined jobs, and they run Spark in different places:

- **Ingestion jobs** run Spark on the local machine and write Unity Catalog tables from outside Databricks. They use [DatabricksExternalRunner](external-runner.md) with `format: iceberg` and `catalog: data_platform`.
- **Refined jobs** run inside a Databricks cluster through [DatabricksConnectRunner](connect-runner.md). They read the tables written by the ingestion jobs and write new ones.

Run the ingestion jobs of a scenario before its refined jobs, which read the tables they write.

## Before Running

The jobs read the Databricks workspace and credentials from environment variables:

- `DATABRICKS_HOST`: the Databricks workspace URL.
- `DATABRICKS_CLIENT_ID`: the client ID of the service principal.
- `DATABRICKS_CLIENT_SECRET`: the client secret of the service principal.
- `DATABRICKS_CLUSTER_ID`: the ID of the cluster that executes the job. Only the refined jobs use it.

Export them before running a job:

```bash
export DATABRICKS_HOST="https://my-workspace.cloud.databricks.com"
export DATABRICKS_CLIENT_ID="my-client-id"
export DATABRICKS_CLIENT_SECRET="my-client-secret"
export DATABRICKS_CLUSTER_ID="0123-456789-abcdefgh"
```

The ingestion jobs use [DatabricksExternalRunner](external-runner.md), which requires the `tio_spark` extra. The refined jobs use [DatabricksConnectRunner](connect-runner.md), which requires the `connect` extra. The two extras cannot be combined in one environment. See [Installation](index.md#installation).

The ingestion jobs also need external access to Unity Catalog. See [Before Running a Job](external-runner.md#before-running-a-job) for the metastore setting and the grant the service principal needs.

The input paths in the ingestion jobs, such as `examples/data/ecommerce/customers.csv`, are relative to the repository root. Run the jobs from there.

## Two Transform Styles

The examples show two approaches to business logic:

- **SQL transforms** ([SparkSqlTransform](https://github.com/fdmorison/tiozin/blob/main/docs/tio_spark/sql-transform.md)): logic lives in the query, and the plugin is generic. The ecommerce examples follow this pattern.
- **Plugin transforms** (`SparkWordCountTransform`): logic is encapsulated in the plugin class, and the YAML only declares parameters. The Shakespeare refined jobs follow this pattern, after a SQL transform that selects one work.

## Ecommerce

A two-step pipeline split across three jobs: raw ingestion for customers and orders, followed by a refined join. The ingestion jobs read CSV files with [SparkFileInput](https://github.com/fdmorison/tiozin/blob/main/docs/tio_spark/file-input.md). The refined job reads the raw tables with [SparkTableInput](https://github.com/fdmorison/tiozin/blob/main/docs/tio_spark/table-input.md). All three write [Apache Iceberg](https://iceberg.apache.org/) tables with [SparkTableOutput](https://github.com/fdmorison/tiozin/blob/main/docs/tio_spark/table-output.md).

| File | What it shows |
|---|---|
| [`ecommerce/ingestion_customer_job.yaml`](../examples/jobs/ecommerce/ingestion_customer_job.yaml) | CSV ingestion with `SparkFileInput`, ingestion metadata added with `SparkSqlTransform`, and output to `data_platform.default.raw_storefront_customers` with `mode: merge`, `merge_keys: id`, and `merge_exclude_fields: [created_at, _raw_created_at]`, partitioned by `days(created_at)` |
| [`ecommerce/ingestion_orders_job.yaml`](../examples/jobs/ecommerce/ingestion_orders_job.yaml) | Same ingestion pattern for orders, written to `data_platform.default.raw_storefront_orders` with `mode: merge`, `merge_keys: id`, and `merge_exclude_fields: [created_at, _raw_created_at]`, partitioned by `days(created_at)` |
| [`ecommerce/refined_orders_job.yaml`](../examples/jobs/ecommerce/refined_orders_job.yaml) | Both raw tables read with `SparkTableInput`, joined in SQL, chained transforms with `@data`, a parameterized query with `args:`, and output to `data_platform.default.refined_storefront_high_value_orders` with `mode: truncate`, partitioned by `days(created_at)` |

Run both ingestion jobs before `refined_orders_job.yaml`:

```bash
tiozin run examples/jobs/ecommerce/ingestion_customer_job.yaml
tiozin run examples/jobs/ecommerce/ingestion_orders_job.yaml
tiozin run examples/jobs/ecommerce/refined_orders_job.yaml
```

## Shakespeare

A multi-job pipeline using works of Shakespeare as the source dataset. An ingestion job loads the raw texts into one table. Each refined job then counts the words of one work independently, so a collection of independent jobs composes into a larger pipeline.

| File | What it shows |
|---|---|
| [`shakespeare/ingestion_job.yaml`](../examples/jobs/shakespeare/ingestion_job.yaml) | Text ingestion from `examples/data/shakespeare` with `SparkFileInput`, `format: text`, and `explode_filepath: true`, written to `data_platform.default.raw_shakespeare_shakespeare` with `mode: overwrite`, partitioned by `filestem` |
| [`shakespeare/refined_hamlet_job.yaml`](../examples/jobs/shakespeare/refined_hamlet_job.yaml) | Raw table read with `SparkTableInput`, Hamlet selected by `filestem` with `SparkSqlTransform`, word count with `SparkWordCountTransform`, and output to `data_platform.default.refined_shakespeare_hamlet` with `mode: truncate` |
| [`shakespeare/refined_sonnets_job.yaml`](../examples/jobs/shakespeare/refined_sonnets_job.yaml) | Word count of the Sonnets |
| [`shakespeare/refined_kinglear_job.yaml`](../examples/jobs/shakespeare/refined_kinglear_job.yaml) | Word count of King Lear |
| [`shakespeare/refined_loverscomplaint_job.yaml`](../examples/jobs/shakespeare/refined_loverscomplaint_job.yaml) | Word count of A Lover's Complaint |

Run the ingestion job before any refined job:

```bash
tiozin run examples/jobs/shakespeare/ingestion_job.yaml
tiozin run examples/jobs/shakespeare/refined_hamlet_job.yaml
```
