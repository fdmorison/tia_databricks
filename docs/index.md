# tia_databricks

`tia_databricks` is the Tiozin family for [Databricks](https://docs.databricks.com/). A family is an installable package of Tiozin plugins that share the same runtime. See [The Family Model](https://github.com/fdmorison/tiozin/blob/main/docs/concepts/family.md) for how families fit into Tiozin.

[Installation](installation.md) covers the extras and how to add the package to a project. [Getting Started](getting-started.md) sets up the example settings and the Databricks workspace.

## Plugins

- [DatabricksConnectRunner](connect-runner.md): runs Spark jobs inside a Databricks cluster through Databricks Connect. Requires the `connect` extra.
- [DatabricksExternalRunner](external-runner.md): runs Spark jobs locally that read and write Unity Catalog tables from outside Databricks. Requires the `tio_spark35` or `tio_spark40` extra, or a separately installed PySpark.

## Using the Plugins in a Job

After installation, the plugins are available by class name in any job:

```yaml
runner:
  kind: DatabricksExternalRunner
  catalog: tiozin
```

The snippets on this page leave out the workspace URL and credentials. With the settings from [Getting Started](getting-started.md), the runner takes them from `runtime_defaults`.

If another installed family defines a class with the same name, qualify the kind with the family name:

```yaml
runner:
  kind: tia_databricks:DatabricksExternalRunner
  catalog: tiozin
```

## Passing Spark Config Options

[Spark config options](https://spark.apache.org/docs/latest/configuration.html) go directly in the runner:

```yaml
runner:
  kind: DatabricksExternalRunner
  catalog: tiozin
  spark.executor.memory: 4g
  spark.sql.shuffle.partitions: 200
```

Each runner page explains how it applies them: [DatabricksConnectRunner](connect-runner.md#passing-spark-config-options) and [DatabricksExternalRunner](external-runner.md#passing-spark-config-options).

## Examples

[Examples](examples.md) lists the example jobs in this repository, which ingest and refine Unity Catalog tables.

## Working With tio_spark

[DatabricksConnectRunner](connect-runner.md) extends [SparkRunner](https://github.com/fdmorison/tio_spark/blob/main/docs/runner.md) from the [tio_spark](https://github.com/fdmorison/tio_spark/blob/main/docs/index.md) family, so it executes the Spark plans produced by `tio_spark` steps. The `tio_spark` steps ship in the `tio_spark` package, which `tia_databricks` installs.

With the `connect` extra, Databricks Connect provides the PySpark those steps run on. With the `tio_spark35` or `tio_spark40` extra, `tio_spark[pyspark35]` or `tio_spark[pyspark40]` provides it. Without an extra, `tia_databricks` installs no PySpark, so the environment provides it.
