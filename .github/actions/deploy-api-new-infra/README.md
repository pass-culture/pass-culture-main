# Deploy API New Infrastructure Action

This is a composite GitHub Action that handles the deployment of the Pass Culture API using the new infrastructure setup with Argo Workflows.

## Description

This action deploys the Pass Culture API to the new infrastructure by:
- Installing kubectl CLI tool
- Setting up Argo Workflows CLI
- Authenticating with Google Cloud Platform using OIDC
- Connecting to the target GKE cluster
- Running an Argo Workflow template to perform the full deployment

## Inputs

| Input | Description | Required | Default | Type |
|-------|-------------|----------|---------|------|
| `environment` | Target environment for deployment | Yes | | `string` |
| `app_version` | Application version to deploy | Yes | | `string` |
| `location` | GCP region/location of the cluster | No | `europe-west9` | `string` |
| `cluster_name` | Name of the GKE cluster | No | | `string` |
| `gcp_project_id` | Google Cloud Project ID | No | | `string` |
| `GCP_EHP_WORKLOAD_IDENTITY_PROVIDER` | GCP workload identity provider for authentication | Yes | | `string` |
| `GCP_EHP_SERVICE_ACCOUNT` | GCP service account for authentication | Yes | | `string` |

## Usage

```yaml
- name: "Deploy API with New Infrastructure"
  uses: ./.github/actions/deploy-api-new-infra
  with:
    environment: ${{ inputs.environment }}
    app_version: ${{ inputs.app_version }}
    location: ${{ inputs.location }}
    cluster_name: ${{ inputs.cluster_name }}
    gcp_project_id: ${{ inputs.gcp_project_id }}
    GCP_EHP_WORKLOAD_IDENTITY_PROVIDER: ${{ secrets.GCP_EHP_WORKLOAD_IDENTITY_PROVIDER }}
    GCP_EHP_SERVICE_ACCOUNT: ${{ secrets.GCP_EHP_SERVICE_ACCOUNT }}
```

## Required Permissions

The job using this action should have the following permissions:
- `id-token: write` - For OIDC authentication with Google Cloud
- `contents: read` - For checking out the repository

## Prerequisites

1. **GKE Cluster**: A Google Kubernetes Engine cluster must exist with the specified name and location
2. **Argo Workflows**: The target cluster must have Argo Workflows installed and configured
3. **Workflow Template**: The workflow template `wfw-pcapi-full-deploy` must exist in the target cluster
4. **Service Account**: The GCP service account must have appropriate permissions to:
   - Access the GKE cluster
   - Run Argo Workflows
   - Deploy to the target environment

## Workflow Template

This action submits an Argo Workflow using the template `wfw-pcapi-full-deploy` with the following parameters:
- `environment`: The target deployment environment
- `version`: The application version to deploy

## Dependencies

This action depends on several external actions and tools:
- `azure/setup-kubectl@v4` - For installing kubectl
- `google-github-actions/auth@v3` - For GCP authentication
- `google-github-actions/get-gke-credentials@v3` - For GKE cluster authentication
- Argo Workflows CLI v3.6.5 - Downloaded and installed during execution

## Namespace

The action connects to the GKE cluster using the `infra-cd-prd` namespace and uses DNS-based endpoints for improved connectivity.

## Error Handling

The Argo Workflow submission includes:
- `--log`: Real-time log streaming
- `--wait`: Waits for workflow completion before returning

If the workflow fails, the action will fail accordingly, providing visibility into deployment issues.

## Notes

- This action is specifically designed for the new infrastructure setup
- It replaces the traditional Helm-based deployment approach with Argo Workflows
- The workflow template handles all deployment logic including migrations, manifest updates, and service synchronization