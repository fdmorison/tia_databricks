# Installation

`tia_databricks` is installed as a Python dependency. It requires Python 3.11 or later and installs [tio_spark](https://github.com/fdmorison/tio_spark/blob/main/docs/index.md) 0.1.3 or later, which brings [Tiozin](https://github.com/fdmorison/tiozin) 6.0.0 or later. Tiozin discovers the family automatically, so its plugins are available by class name in job YAML right after installation.

The package installs `tio_spark` without PySpark. Its extras add what each place Spark runs needs: `connect` for a Databricks cluster, and `tio_spark35` or `tio_spark40` for the local machine.

## Running Spark on a Databricks Cluster

The `connect` extra is for running Spark on a Databricks cluster with [DatabricksConnectRunner](connect-runner.md). It installs [Databricks Connect](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/), which ships its own PySpark.

```bash
pip install "tia_databricks[connect]"
```

The installed Databricks Connect version must match the cluster's Databricks Runtime. See [Matching the Databricks Connect Version](connect-runner.md#matching-the-databricks-connect-version).

## Running Spark Locally

[DatabricksExternalRunner](external-runner.md) runs Spark on the local machine, so it needs [PySpark](https://spark.apache.org/docs/latest/api/python/) installed there. Two extras bring a pinned PySpark line:

- `tio_spark35`: installs `tio_spark[pyspark35]`, with PySpark 3.5.x.
- `tio_spark40`: installs `tio_spark[pyspark40]`, with PySpark 4.0.x.

```bash
pip install "tia_databricks[tio_spark35]"
```

## Using a Separately Installed PySpark

Without an extra, the package installs `tio_spark` without PySpark. This plain install fits environments that already provide PySpark or that pin their own PySpark version.

```bash
pip install tia_databricks
```

If the environment does not provide PySpark yet, install it alongside the package before running [DatabricksExternalRunner](external-runner.md).

## Keeping the Extras Apart

`tio_spark35` and `tio_spark40` cannot be combined.

`connect` cannot be combined with `tio_spark35` or `tio_spark40`. Install it in an environment without a separate `pyspark` package as well.

## Matching Tiozin and tio_spark

The install options mirror the ones in Tiozin and `tio_spark`:

| tia_databricks | Tiozin | tio_spark |
|---|---|---|
| `tia_databricks` | `tiozin[tio_spark]` | `tio_spark` |
| `tia_databricks[tio_spark35]` | `tiozin[tio_spark35]` | `tio_spark[pyspark35]` |
| `tia_databricks[tio_spark40]` | `tiozin[tio_spark40]` | `tio_spark[pyspark40]` |

See the [tio_spark installation guide](https://github.com/fdmorison/tio_spark/blob/main/docs/installation.md) for the PySpark versions behind each extra.

## Adding It to a Project

Add the package to the project's dependencies, with the extra that matches where Spark runs, such as in `pyproject.toml`:

```toml
[project]
dependencies = [
  "tia_databricks[connect]",
]
```

## Next Steps

- [Getting Started](getting-started.md): set up the example settings and the Databricks workspace.
- [Examples](examples.md): run the example jobs.
- [tia_databricks family](index.md): the plugins and how to use them in a job.
