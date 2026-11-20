# Getting Started

The example jobs connect to Databricks through settings in the `tiozin.yaml` file and credentials in the `.env` file. Set both up once, then check what each runner needs on the Databricks side.

Start with `tia_databricks` installed as described in [Installation](installation.md).

## Setting Up tiozin.yaml

Tiozin reads its [settings](https://github.com/fdmorison/tiozin/blob/main/docs/settings/index.md) from the `tiozin.yaml` file. The file configures [registries](https://github.com/fdmorison/tiozin/blob/main/docs/settings/index.md#registries), such as the job and schema registries, and default plugin arguments under [`runtime_defaults`](https://github.com/fdmorison/tiozin/blob/main/docs/settings/index.md#runtime-defaults).

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

   A job that leaves these fields out takes them from here. The values come from the variables filled in the `.env` file in step 1.

## Preparing the Workspace

Each runner also has requirements on the Databricks side, such as a cluster that [DatabricksConnectRunner](connect-runner.md) can attach to and external access to [Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/) for [DatabricksExternalRunner](external-runner.md). Check them before the first run:

- [Before running a job with DatabricksConnectRunner](connect-runner.md#before-running-a-job)
- [Before running a job with DatabricksExternalRunner](external-runner.md#before-running-a-job)

## Next Steps

- [Examples](examples.md): run the example jobs.
- [DatabricksConnectRunner](connect-runner.md) and [DatabricksExternalRunner](external-runner.md): all runner parameters.
- [Tiozin Settings Guide](https://github.com/fdmorison/tiozin/blob/main/docs/settings/index.md): everything the `tiozin.yaml` file can configure.
