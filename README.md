# tia_databricks

`tia_databricks` is the Databricks family for [Tiozin](https://github.com/fdmorison/tiozin). It provides Tiozin plugins that run data jobs on [Databricks](https://docs.databricks.com/).

A family is an installable package of Tiozin plugins that share the same runtime. See [The Family Model](https://github.com/fdmorison/tiozin/blob/main/docs/concepts/family.md) for how families fit into Tiozin.

## Usage

After installation, its plugins are available by class name in any job:

```yaml
runner:
  kind: DatabricksExternalRunner
  catalog: tiozin
```

If another installed family defines a class with the same name, qualify the kind with the family name:

```yaml
runner:
  kind: tia_databricks:DatabricksExternalRunner
  catalog: tiozin
```

Spark config options go directly in the runner:

```yaml
runner:
  kind: DatabricksExternalRunner
  catalog: tiozin
  spark.executor.memory: 4g
  spark.sql.shuffle.partitions: 200
```

## Installation

`tia_databricks` is installed as a Python dependency. Once it is installed, its plugins are available in any job.

The package provides two extras, `connect` and `tio_spark`, and a project installs only one of them, depending on where Spark runs.

The `connect` extra is for running Spark on a Databricks cluster with [DatabricksConnectRunner](https://github.com/fdmorison/tia_databricks/blob/main/docs/connect-runner.md). It installs [Databricks Connect](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/).

```bash
pip install "tia_databricks[connect]"
```

The `tio_spark` extra is for running Spark on the local machine with [DatabricksExternalRunner](https://github.com/fdmorison/tia_databricks/blob/main/docs/external-runner.md). It installs `tiozin[tio_spark]`, which brings PySpark.

```bash
pip install "tia_databricks[tio_spark]"
```

Add it to the project's dependencies, such as in `pyproject.toml`:

```toml
[project]
dependencies = [
  "tia_databricks[connect]",
]
```

The two extras cannot be combined. Databricks Connect ships its own PySpark, so install `connect` in an environment without `tiozin[tio_spark]` or a separate `pyspark` package.

## Setting Up tiozin.yaml

`tiozin.yaml` is the [Tiozin settings file](https://github.com/fdmorison/tiozin/blob/main/docs/settings/index.md). It configures [registries](https://github.com/fdmorison/tiozin/blob/main/docs/settings/index.md#registries), such as the job and schema registries, and default plugin arguments under [`runtime_defaults`](https://github.com/fdmorison/tiozin/blob/main/docs/settings/index.md#runtime-defaults).

The example settings use `runtime_defaults` to connect the runners to Databricks.

1. Copy the `.env.example` file to `.env` at the repository root, then fill in the Databricks variables in the `.env` file. The `.env` file is gitignored.

   ```bash
   cp .env.example .env
   ```

2. Copy the `tiozin.example.yaml` file to `tiozin.yaml` at the repository root. The `tiozin.yaml` file is gitignored.

   ```bash
   cp tiozin.example.yaml tiozin.yaml
   ```

3. Find the runner connection settings under `runtime_defaults`. They give each runner the workspace URL and service principal credentials, and DatabricksConnectRunner also gets the cluster ID. Each value is read from an environment variable:

   ```yaml
   runtime_defaults:

     - kind: DatabricksConnectRunner
       host: "{{ ENV.DATABRICKS_HOST }}"
       cluster_id: "{{ ENV.DATABRICKS_CLUSTER_ID }}"
       client_id: "{{ ENV.DATABRICKS_CLIENT_ID }}"
       client_secret: "{{ ENV.DATABRICKS_CLIENT_SECRET }}"

     - kind: DatabricksExternalRunner
       host: "{{ ENV.DATABRICKS_HOST }}"
       client_id: "{{ ENV.DATABRICKS_CLIENT_ID }}"
       client_secret: "{{ ENV.DATABRICKS_CLIENT_SECRET }}"
   ```

   A job that leaves these fields out takes them from here. The values come from the variables filled in `.env` in step 1.

## Preparing the Workspace

Each runner also has requirements on the Databricks side, such as a cluster that [DatabricksConnectRunner](https://github.com/fdmorison/tia_databricks/blob/main/docs/connect-runner.md) can attach to and external access to Unity Catalog for [DatabricksExternalRunner](https://github.com/fdmorison/tia_databricks/blob/main/docs/external-runner.md). Check them before the first run:

- [Before running a job with DatabricksConnectRunner](https://github.com/fdmorison/tia_databricks/blob/main/docs/connect-runner.md#before-running-a-job)
- [Before running a job with DatabricksExternalRunner](https://github.com/fdmorison/tia_databricks/blob/main/docs/external-runner.md#before-running-a-job)

## Plugins

- [DatabricksConnectRunner](https://github.com/fdmorison/tia_databricks/blob/main/docs/connect-runner.md): runs Spark jobs inside a Databricks cluster through Databricks Connect. Requires the `connect` extra.
- [DatabricksExternalRunner](https://github.com/fdmorison/tia_databricks/blob/main/docs/external-runner.md): runs Spark jobs locally that read and write Unity Catalog tables from outside Databricks. Requires the `tio_spark` extra.

The [family documentation](https://github.com/fdmorison/tia_databricks/blob/main/docs/index.md) lists every plugin page.

## Learn More

- [Examples](https://github.com/fdmorison/tia_databricks/blob/main/docs/examples.md)
- [Tiozin](https://github.com/fdmorison/tiozin)
- [Databricks Connect](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/)
