# tia_databricks

`tia_databricks` is the Tiozin family for [Databricks](https://docs.databricks.com/). A family is an installable package of Tiozin plugins that share the same runtime. See [The Family Model](https://github.com/fdmorison/tiozin/blob/main/docs/concepts/family.md) for how families fit into Tiozin.

## Installation

The package requires Python 3.11 or later and installs Tiozin 4.x as a dependency. Tiozin discovers the family automatically through the `tiozin.family` entry point, so its plugins are available by class name in job YAML right after installation.

To run jobs on a Databricks cluster, install the `connect` extra. It installs [Databricks Connect](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/):

```bash
pip install "tia_databricks[connect]"
```

To run Spark locally, install the `tio_spark` extra. It installs `tiozin[tio_spark]`, which brings a local PySpark. With only this extra, the family currently provides no plugins:

```bash
pip install "tia_databricks[tio_spark]"
```

The two extras cannot be combined. Databricks Connect ships its own PySpark, so the `connect` extra must go in an environment without `tiozin[tio_spark]` or a separate `pyspark` package.

## Plugins

- [DatabricksConnectRunner](connect-runner.md): runs Spark jobs inside a Databricks cluster through Databricks Connect. Requires the `connect` extra.

## Working With tio_spark

[DatabricksConnectRunner](connect-runner.md) extends [SparkRunner](https://github.com/fdmorison/tiozin/blob/main/docs/tio_spark/runner.md) from the [tio_spark](https://github.com/fdmorison/tiozin/blob/main/docs/tio_spark/index.md) family, so it executes the Spark plans produced by `tio_spark` steps. The `tio_spark` steps ship inside the `tiozin` package.

With the `connect` extra, Databricks Connect provides the PySpark those steps run on. With the `tio_spark` extra, `tiozin[tio_spark]` provides it.
