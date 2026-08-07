<!-- hy-mt2-i18n:start -->
[Español](./README.md) | [中文](./README_zh-CN.md) | **English** | [日本語](./README_ja.md)
<!-- hy-mt2-i18n:end -->

<div align=center>
  <img src="https://storage.googleapis.com/passculture-metier-prod-production-assets-fine-grained/assets/passculture.gif" style="width: 360px">
  <br />
  <a href="https://apps.apple.com/fr/app/pass-culture/id1557887412">
    <img src="https://upload.wikimedia.org/wikipedia/commons/4/40/Download_on_the_App_Store_Badge_FRCA_RGB_blk.svg" style="height: 50px">
  </a>
  <a href="https://play.google.com/store/apps/details?id=app.passculture.webapp&hl=fr">
    <img src="https://upload.wikimedia.org/wikipedia/commons/8/8e/Google_Play_Store_badge_FR.svg" style="height: 50px; padding-left: 12px">
  </a>
</div>

---

The `main` repository contains the following 4 projects:

- The backend: [api](./api) (Flask)  
- The partner area: [pro](./pro) (React)  
- Documentation for the public API for Pass Culture’s technical partners: [doc](./api/documentation)  
- Maintenance page (HTML): [maintenance-site](./maintenance-site)

## Installation

### Installing common dependencies for the front-end and back-end

- [safe-chain](https://www.npmjs.com/package/@aikidosec/safe-chain) # TODO: test the installation with safe-chain
  - `npm i -g @aikidosec/safe-chain`
  - `safe-chain setup`
  - Restart the terminal

- [Commitizen](https://commitizen-tools.github.io/commitizen/#installation) (CLI for writing commits in the correct format)
  - `brew install commitizen`

- [gitleaks](https://github.com/gitleaks/gitleaks)
  - `brew install gitleaks`

- [semgrep](https://semgrep.dev/)
  - `brew install semgrep`

### Installing All Projects

You will need an SSH key in your GitHub profile to clone the repository.

1. `git clone git@github.com:pass-culture/pass-culture-main.git pass-culture-main`
2. `cd pass-culture-main`
3. `sudo./pc symlink`
4. `pc install`

The READMEs for each sub-project will detail their specific installation processes.

- [README.md api](./api#readme)
- [README.md pro](./pro#readme)

### Starting Applications via the `pc` Script

It is recommended to read the READMEs in the paragraph above for server installation and startup. However, if you’re short on time, here are brief instructions for launching the API and various frontends via the `pc` script, which relies on docker compose.

The `pc` script is not essential to the project; it is still possible to start the servers directly using the `python` or `pnpm` commands.

#### Backend API

Using Docker and the `pc` script:

- [docker](https://docs.docker.com/install/) (tested with 19.03.12)
- [docker compose (included with Docker Desktop)](https://docs.docker.com/compose/install/#install-compose) (tested with 1.26.2)

- `pc start-backend` or `pc start-backend --fast` or `pc start-proxy-backend` or `pc start-proxy-backend --fast`
- `pc sandbox -n industrial` (to populate the DB)

The backend is accessible at [http://localhost:5001/](http://localhost:5001/), and its functionality can be tested via the endpoint [http://localhost:5001/health/api](http://localhost:5001/health/api).

A major drawback of using Docker is the latency and time it takes to build the image. Other ways to start the backend are outlined in the [`api`](./api#readme) [README].

#### Backoffice

- [http://localhost:5002/](http://localhost:5002/) should be launched and functional after `pc start-backend`, once the API responds.
- Click on _Sign in with Google_.
- You will then be taken to the BO’s homepage as the admin user `admin@passculture.local`, with all permissions.
- If you need a specific email address for the local admin, for example for linking to external services, specify the email in a variable `BACKOFFICE_LOCAL_USER_EMAIL` in the file `.env.local.secret`.

#### Pro Portal

- `pc start-pro`
- [http://localhost:3001/](http://localhost:3001/) should be launched and functional
- Log in using `pctest.admin93.0@example.com` (admin) or `pctest.pro93.0@example.com` (non-admin)

The password for sandbox users in the development environment is: `user@AZERTY123`

The cloud-deployed test environment (_testing_) uses a secret password to protect the data processed during testing; internally, the password “PRO - testing” is available in the team’s vault.

These users also exist for version 97, by replacing `93` with `97`.

More information is available in the [Pro README](./pro/README.md).

### Useful Commands

- Rebuild: `pc rebuild-backend` (rebuild the Docker image without caching)  
- Restart: `pc restart-backend` (erase the database and restart all containers)  
- Restore: `pc restore-db file.pgdump` (restore a PostgreSQL dump file (file.pgdump) locally)

### Troubleshooting

If the `sandbox` command returns errors that I cannot resolve, we can try deleting and rebuilding its local database via `pc restart-backend`. Otherwise:

- Stop the running containers
- `docker rm -f pc-postgres` <= Remove the container
- `docker volume rm pass-culture-main_postgres_data` <= Delete the data
- `pc start-backend`
- `pc sandbox -n industrial`

## Deployment

### Deploying to the Testing Environment

The `master` branch is deployed to testing every hour.

### Deploying to a Preview Environment

It is necessary to have the [github CLI](https://cli.github.com/) installed.

To deploy to a preview environment, use the command `pc deploy-preview` (complete documentation is available in the [pc](./pc) script).

### Deploying to Staging, Production, and Integration Environments

Deployment is triggered via GitHub actions (specifically `release--build`, `release--deploy.yml`, `release--build.yml`, `release--build-hotfix.yml`) and is documented in Notion (article Tag-MES-et-MEP).

To check the version number of the deployed API:

```
https://backend.staging.passculture.team/health/api
https://backend.passculture.app/health/api
```

## Administration # TODO: migrate the documentation to the new infrastructure

### Connecting to a PostgreSQL database in an environment

```bash
pc -e <testing|staging|production|integration> psql
```

or

```bash
pc -e <testing|staging|production|integration> pgcli
```

### Connecting to the local PostgreSQL database

```bash
pc -e <testing|staging|production|integration> psql
```

or

```bash
pc -e <testing|staging|production|integration> pgcli
```

### Connecting to a Python environment via command line (testing | staging | production | integration)

```bash
pc -e <testing|staging|production|integration> python
```

### Uploading a File

It is also possible to upload a file to the temporary environment at the path `/usr/src/app/myfile.extension`.

```bash
pc -e <testing|staging|production|integration> -f myfile.extension python
```

```bash
pc -e <testing|staging|production|integration> -f myfile.extension bash
```

### Accessing database logs

Locally:

```bash
pc access-db-logs
```

In other environments:

```bash
pc -e <testing|staging|production> access-db-logs
```
