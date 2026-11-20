# Installation

`tia_databricks` is installed as a Python dependency. It requires Python 3.11 or later and installs Tiozin 4.1 or a later 4.x release. Tiozin discovers the family automatically, so its plugins are available by class name in job YAML right after installation.

The package provides two extras, `connect` and `tio_spark`, and a project installs only one of them, depending on where Spark runs.

## Running Spark on a Databricks Cluster

The `connect` extra is for running Spark on a Databricks cluster with [DatabricksConnectRunner](connect-runner.md). It installs [Databricks Connect](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/).

```bash
pip install "tia_databricks[connect]"
```

The installed Databricks Connect version must match the cluster's Databricks Runtime. See [Matching the Databricks Connect Version](connect-runner.md#matching-the-databricks-connect-version).

## Running Spark Locally

The `tio_spark` extra is for running Spark on the local machine with [DatabricksExternalRunner](external-runner.md). It installs `tiozin[tio_spark]`, which brings [PySpark](https://spark.apache.org/docs/latest/api/python/).

```bash
pip install "tia_databricks[tio_spark]"
```

## Keeping the Extras Apart

The two extras cannot be combined. Databricks Connect ships its own PySpark, so install `connect` in an environment without `tiozin[tio_spark]` or a separate `pyspark` package.

## Adding It to a Project

Add the package with one extra to the project's dependencies, such as in `pyproject.toml`:

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
