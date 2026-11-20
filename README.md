# tia_databricks

`tia_databricks` is the Databricks family for [Tiozin](https://github.com/fdmorison/tiozin), with Tiozin plugins that run data jobs on [Databricks](https://docs.databricks.com/). See [The Family Model](https://github.com/fdmorison/tiozin/blob/main/docs/concepts/family.md) for how families fit into Tiozin.

## One-Minute Example

```bash
pip install "tia_databricks[tio_spark35]"
```

This job loads the text of Hamlet into a Unity Catalog table with [DatabricksExternalRunner](https://github.com/fdmorison/tia_databricks/blob/main/docs/external-runner.md):

```yaml
kind: LinearJob
name: ingestion_hamlet_job
owner: literature@tiozin.com
maintainer: tiozin
cost_center: tio_scrooge

org: tiozin
region: latam
domain: literature
subdomain: classics
product: shakespeare
model: hamlet
layer: raw

runner:
  kind: DatabricksExternalRunner
  host: "{{ ENV.DATABRICKS_HOST }}"
  client_id: "{{ ENV.DATABRICKS_CLIENT_ID }}"
  client_secret: "{{ ENV.DATABRICKS_CLIENT_SECRET }}"
  format: iceberg
  catalog: tiozin

inputs:
  - kind: SparkFileInput
    name: load_hamlet
    path: examples/data/{{product}}/{{model}}.txt
    format: text

outputs:
  - kind: SparkTableOutput
    name: save_hamlet
    table: tiozin.default.{{layer}}_{{product}}_{{model}}
    format: iceberg
    mode: overwrite
```

Run it:

```bash
tiozin run examples/jobs/oneminute.yaml
```

## Plugins

- [DatabricksConnectRunner](https://github.com/fdmorison/tia_databricks/blob/main/docs/connect-runner.md): runs Spark jobs inside a Databricks cluster through Databricks Connect. Requires the `connect` extra.
- [DatabricksExternalRunner](https://github.com/fdmorison/tia_databricks/blob/main/docs/external-runner.md): runs Spark jobs locally that read and write Unity Catalog tables from outside Databricks. Requires the `tio_spark35` or `tio_spark40` extra, or a separately installed PySpark.

## Documentation

### Getting Started
- [Installation](https://github.com/fdmorison/tia_databricks/blob/main/docs/installation.md)
- [Getting Started](https://github.com/fdmorison/tia_databricks/blob/main/docs/getting-started.md)
- [Examples](https://github.com/fdmorison/tia_databricks/blob/main/docs/examples.md)

### Plugins
- [The tia_databricks Family](https://github.com/fdmorison/tia_databricks/blob/main/docs/index.md)
- [DatabricksConnectRunner](https://github.com/fdmorison/tia_databricks/blob/main/docs/connect-runner.md)
- [DatabricksExternalRunner](https://github.com/fdmorison/tia_databricks/blob/main/docs/external-runner.md)

### Learn More
- [Tiozin](https://github.com/fdmorison/tiozin)
- [Tiozin Settings Guide](https://github.com/fdmorison/tiozin/blob/main/docs/settings/index.md)
- [Databricks Connect](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/)

## License

This project is licensed under the [Mozilla Public License 2.0](https://github.com/fdmorison/tia_databricks/blob/main/LICENSE).
