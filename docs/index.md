# tia_databricks

`tia_databricks` is the Tiozin family for [Databricks](https://docs.databricks.com/). A family is an installable package of Tiozin plugins that share the same runtime. See [The Family Model](https://github.com/fdmorison/tiozin/blob/main/docs/concepts/family.md) for how families fit into Tiozin.

## Installation

```bash
pip install tia_databricks
```

The package requires Python 3.11 or later and installs Tiozin 4.x as a dependency. Tiozin discovers the family automatically through the `tiozin.family` entry point, so its plugins are available by class name in job YAML right after installation.

`tia_databricks` depends on [Databricks Connect](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/), which ships its own PySpark. Install it in an environment without `tiozin[tio_spark]` or a separate `pyspark` package.

## Plugins

- [DatabricksConnectRunner](connect-runner.md): runs Spark jobs inside a Databricks cluster through Databricks Connect.

## Working With tio_spark

[DatabricksConnectRunner](connect-runner.md) extends [SparkRunner](https://github.com/fdmorison/tiozin/blob/main/docs/tio_spark/runner.md) from the [tio_spark](https://github.com/fdmorison/tiozin/blob/main/docs/tio_spark/index.md) family, so it executes the Spark plans produced by `tio_spark` steps. The `tio_spark` steps ship inside the `tiozin` package. Databricks Connect provides the PySpark they run on.
