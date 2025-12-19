# Deploy API Action

This is a composite GitHub Action that handles the deployment of the Pass Culture API to Kubernetes environments.

## Description

This action encapsulates all the steps required to deploy the Pass Culture API, including:
- Authentication with Google Cloud Platform
- Docker registry authentication
- GitHub app authentication for repository access
- Kubernetes cluster connection
- Pre-deployment migrations
- Helm chart updates
- Manifest rendering and pushing
- ArgoCD synchronization
- ~~Post-deployment migrations~~

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `environment` | Target environment for deployment | Yes | |
| `app_version` | Application version to deploy | Yes | |
| `cluster_scope` | Cluster scope | No | `metier` |
| `cluster_environment` | Cluster environment | No | `ehp` |
| `workload_identity_provider_secret_name` | Workload identity provider secret name | Yes | |
| `gcp_ehp_workload_identity_provider` | GCP EHP workload identity provider | Yes | |
| `gcp_ehp_service_account` | GCP EHP service account | Yes | |
| `passculture_github_action_app_id` | GitHub Application ID to use to clone other repos | Yes | |
| `passculture_github_action_app_private_key` | Private key for the GitHub application used to clone other repos | Yes | |

## Usage

```yaml
- name: "Deploy API"
  uses: ./.github/actions/deploy-api
  with:
    environment: ${{ inputs.environment }}
    app_version: ${{ inputs.app_version }}
    cluster_scope: ${{ inputs.cluster_scope }}
    cluster_environment: ${{ inputs.cluster_environment }}
    workload_identity_provider_secret_name: ${{ inputs.workload_identity_provider_secret_name }}
    gcp_ehp_workload_identity_provider: ${{ secrets.GCP_EHP_WORKLOAD_IDENTITY_PROVIDER }}
    gcp_ehp_service_account: ${{ secrets.GCP_EHP_SERVICE_ACCOUNT }}
    passculture_github_action_app_id: ${{ secrets.PASSCULTURE_GITHUB_ACTION_APP_ID }}
    passculture_github_action_app_private_key: ${{ secrets.PASSCULTURE_GITHUB_ACTION_APP_PRIVATE_KEY }}
```

## Required Permissions

The job using this action should have the following permissions:
- `id-token: write` - For OIDC authentication with Google Cloud
- `contents: read` - For checking out the repository

## Environment

This action should be run in a job with the target environment configured for proper secret access.

## Dependencies

This action depends on several external actions:
- `google-github-actions/auth@v3`
- `google-github-actions/get-secretmanager-secrets@v3`
- `docker/login-action@v3`
- `actions/create-github-app-token@67018539274d69449ef7c02e8e71183d1719ab42`
- `actions/checkout@v5`
- `pass-culture/common-workflows/actions/pc-k8s-connect@pc-k8s-connect/v0.2.0`
- `pass-culture/common-workflows/actions/pcapi-migration@pcapi-migration/v0.2.4`
- `mamezou-tech/setup-helmfile@v2.1.0`
- `pass-culture/common-workflows/actions/setup-pc-render-manifests@setup-pc-render-manifests/v0.1.0`
- `pass-culture/common-workflows/actions/argocd-sync@argocd-sync/v0.8.0`