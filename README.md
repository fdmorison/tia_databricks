# tia_databricks

`tia_databricks` is the Databricks family for [Tiozin](https://github.com/fdmorison/tiozin). It provides Tiozin plugins that run data jobs on [Databricks](https://docs.databricks.com/).

A family is an installable package of Tiozin plugins that share the same runtime. See [The Family Model](https://github.com/fdmorison/tiozin/blob/main/docs/concepts/family.md) for how families fit into Tiozin.

## Installation

The package requires Python 3.11 or later and installs Tiozin 4.x as a dependency. It comes with two extras, one for each place where Spark runs.

To run jobs on a Databricks cluster, install the `connect` extra. It installs [Databricks Connect](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/), which [DatabricksConnectRunner](https://github.com/fdmorison/tia_databricks/blob/main/docs/connect-runner.md) uses to reach the cluster:

```bash
pip install "tia_databricks[connect]"
```

To run Spark locally, install the `spark` extra. It installs `tiozin[tio_spark]`, which brings a local PySpark. With only this extra, the family currently provides no plugins:

```bash
pip install "tia_databricks[spark]"
```

The two extras cannot be combined. Databricks Connect ships its own PySpark, so the `connect` extra must go in an environment without `tiozin[tio_spark]` or a separate `pyspark` package.

## How Tiozin Finds It

Tiozin discovers the family automatically through the `tiozin.family` entry point. The family is registered as `tia_databricks`, and its Python package is `tia_databricks`.

After installation, its plugins are available by class name in any job:

```yaml
runner:
  kind: DatabricksConnectRunner
  host: "{{ ENV.DATABRICKS_HOST }}"
  cluster_id: "{{ ENV.DATABRICKS_CLUSTER_ID }}"
  client_id: "{{ ENV.DATABRICKS_CLIENT_ID }}"
  client_secret: "{{ ENV.DATABRICKS_CLIENT_SECRET }}"
```

If another installed family defines a class with the same name, qualify the kind with the family name:

```yaml
runner:
  kind: tia_databricks:DatabricksConnectRunner
  host: "{{ ENV.DATABRICKS_HOST }}"
  cluster_id: "{{ ENV.DATABRICKS_CLUSTER_ID }}"
  client_id: "{{ ENV.DATABRICKS_CLIENT_ID }}"
  client_secret: "{{ ENV.DATABRICKS_CLIENT_SECRET }}"
```

## Plugins

- [DatabricksConnectRunner](https://github.com/fdmorison/tia_databricks/blob/main/docs/connect-runner.md): runs Spark jobs inside a Databricks cluster through Databricks Connect. Requires the `connect` extra.

The [family documentation](https://github.com/fdmorison/tia_databricks/blob/main/docs/index.md) lists every plugin page.

## Learn More

- [Tiozin](https://github.com/fdmorison/tiozin)
- [Databricks Connect](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/)
