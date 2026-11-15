# tia_databricks

`tia_databricks` is the Databricks family for [Tiozin](https://github.com/fdmorison/tiozin). It provides Tiozin plugins that run data jobs on [Databricks](https://docs.databricks.com/).

A family is an installable package of Tiozin plugins that share the same runtime. See [The Family Model](https://github.com/fdmorison/tiozin/blob/main/docs/concepts/family.md) for how families fit into Tiozin.

## Installation

```bash
pip install tia_databricks
```

The package requires Python 3.11 or later and installs Tiozin 4.x as a dependency.

`tia_databricks` depends on [Databricks Connect](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/), which ships its own PySpark. Install it in an environment without `tiozin[tio_spark]` or a separate `pyspark` package.

## How Tiozin Finds It

Tiozin discovers the family automatically through the `tiozin.family` entry point. After installation, its plugins are available by class name in any job:

```yaml
runner:
  kind: DatabricksConnectRunner
  host: "{{ ENV.DATABRICKS_HOST }}"
  cluster_id: "{{ ENV.DATABRICKS_CLUSTER_ID }}"
  client_id: "{{ ENV.DATABRICKS_CLIENT_ID }}"
  client_secret: "{{ ENV.DATABRICKS_CLIENT_SECRET }}"
```

## Plugins

- [DatabricksConnectRunner](https://github.com/fdmorison/tia_databricks/blob/main/docs/connect-runner.md): runs Spark jobs inside a Databricks cluster through Databricks Connect.

The [family documentation](https://github.com/fdmorison/tia_databricks/blob/main/docs/index.md) lists every plugin page.

## Learn More

- [Tiozin](https://github.com/fdmorison/tiozin)
- [Databricks Connect](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/)
