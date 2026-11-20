# Examples

The example jobs live in [`examples/jobs/`](../examples/jobs/), with one folder per data product and one YAML per job. Their source data lives in [`examples/data/`](../examples/data/).

Every job reads and writes tables in the `tiozin` catalog of [Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/). All tables are [Apache Iceberg](https://iceberg.apache.org/) tables, written with [SparkTableOutput](https://github.com/fdmorison/tiozin/blob/main/docs/tio_spark/table-output.md).

The scenarios mirror the [Spark examples in Tiozin](https://github.com/fdmorison/tiozin/blob/main/docs/examples.md), adapted to [Databricks](https://docs.databricks.com/).

## Before Running

1. Complete the [setup in the README](../README.md#connecting-to-databricks).
2. Run every job from the repository root.

## Two Kinds of Jobs

- **Ingestion jobs**: Spark runs on the local machine. They use [DatabricksExternalRunner](external-runner.md) and need the `tio_spark` extra.
- **Refined jobs**: Spark runs on a Databricks cluster. They use [DatabricksConnectRunner](connect-runner.md) and need the `connect` extra.

Run the ingestion jobs of a scenario before its refined jobs.

## Ecommerce

Customers and orders are ingested from CSV, then joined into one refined table. The business logic lives in SQL, through [SparkSqlTransform](https://github.com/fdmorison/tiozin/blob/main/docs/tio_spark/sql-transform.md).

| File | What it shows |
|---|---|
| [`ecommerce/ingestion_customer_job.yaml`](../examples/jobs/ecommerce/ingestion_customer_job.yaml) | CSV to a raw table with [SparkFileInput](https://github.com/fdmorison/tiozin/blob/main/docs/tio_spark/file-input.md), `mode: merge` |
| [`ecommerce/ingestion_orders_job.yaml`](../examples/jobs/ecommerce/ingestion_orders_job.yaml) | Same pattern for orders |
| [`ecommerce/refined_orders_job.yaml`](../examples/jobs/ecommerce/refined_orders_job.yaml) | Both raw tables read with [SparkTableInput](https://github.com/fdmorison/tiozin/blob/main/docs/tio_spark/table-input.md), joined in SQL, `mode: truncate` |

```bash
tiozin run examples/jobs/ecommerce/ingestion_customer_job.yaml
tiozin run examples/jobs/ecommerce/ingestion_orders_job.yaml
tiozin run examples/jobs/ecommerce/refined_orders_job.yaml
```

## Shakespeare

One ingestion job loads the texts into a raw table. Each refined job selects one work in SQL and counts its words. The word count lives in a plugin, `SparkWordCountTransform`.

| File | What it shows |
|---|---|
| [`shakespeare/ingestion_job.yaml`](../examples/jobs/shakespeare/ingestion_job.yaml) | Text files to one raw table, `mode: overwrite` |
| [`shakespeare/refined_hamlet_job.yaml`](../examples/jobs/shakespeare/refined_hamlet_job.yaml) | Word count of Hamlet, `mode: truncate` |
| [`shakespeare/refined_sonnets_job.yaml`](../examples/jobs/shakespeare/refined_sonnets_job.yaml) | Word count of the Sonnets |
| [`shakespeare/refined_kinglear_job.yaml`](../examples/jobs/shakespeare/refined_kinglear_job.yaml) | Word count of King Lear |
| [`shakespeare/refined_loverscomplaint_job.yaml`](../examples/jobs/shakespeare/refined_loverscomplaint_job.yaml) | Word count of A Lover's Complaint |

```bash
tiozin run examples/jobs/shakespeare/ingestion_job.yaml
tiozin run examples/jobs/shakespeare/refined_hamlet_job.yaml
```
