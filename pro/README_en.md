# 🚀 pass Culture PRO — App Front-End

<!-- hy-mt2-i18n:start -->
[Español](./README.md) | [中文](./README_zh-CN.md) | **English** | [日本語](./README_ja.md)
<!-- hy-mt2-i18n:end -->


This `/pro` directory contains all the configuration and source code for the web application of the pass Culture professional portal.

**Table of Contents**

- [Prerequisites](#pré-requis)
  - [WSL 2 (Windows only)](#--wsl-2-windows-uniquement)
  - [Git](#-git)
  - [Node.js (via nvm)](#-nodejs-via-nvm)
  - [pnpm](#-pnpm)
  - [Docker](#-docker)
- [Installing the project](#installer-le-projet)
  - [Running the front-end](#lancer-le-front-end)
  - [Sandbox](#sandbox)
- [Developing](#développer)
  - [Configuring your editor](#configurer-son-éditeur)
  - [Testing](#les-tests)
  - [Storybook](#storybook)
  - [Adage](#adage)
  - [Code and architecture standards](#standards-de-code-et-darchitecture)
  - [Technical debt](#dette-technique)
- [Appendices](#annexes)

# Strict Constraints
1. **Structure Lock**: Absolutely maintain the original Markdown data structure, indentation, heading levels, tables, links, URLs, badges, code blocks, and inline codes unchanged.
2. **Selective Translation**: Only translate the visible natural language content intended for users.
3. **Prohibition on Modifications**: It is **strictly forbidden** to translate or alter code tags, key names, variable placeholders (such as {{var}}, ${var}, %s, %d, etc.), command examples, file paths, project names, API names, package names, model names, identifiers, and code symbols; unless a corresponding translation is already provided in the background information.
4. The translations of terms, styles, and proper nouns must be consistent with those in the given background information.

# Prerequisites

## <img src="docs/microsoft-windows-icon.svg" height="20" /> <img src="docs/linux-tux.svg" height="20" /> WSL 2 (Windows only)

For Windows users, it is recommended to use [WSL 2](https://learn.microsoft.com/en-us/windows/wsl/install) with a Linux distribution (such as Ubuntu) to develop on this project.

> **[Install WSL 2](https://learn.microsoft.com/fr-fr/windows/wsl/install)**

## <img src="docs/git-icon.svg" height="20" /> Git

> **[Install Git](https://git-scm.com/downloads)**

It is recommended to use the following configuration for this repository:

# Strict Constraints
1. **Structure Locking**: Absolutely maintain the original Markdown data structure, indentation, heading levels, tables, links, URLs, badges, code blocks, and inline codes unchanged.
2. **Selective Translation**: Only translate visible natural language content intended for users.
3. **Prohibition on Modifications**: It is **strictly forbidden** to translate or alter code tags, key names, variable placeholders (such as {{var}}, ${var}, %s, %d, etc.), command examples, file paths, project names, API names, package names, model names, identifiers, and code symbols; unless a corresponding translation is already provided in the background information.
4. The translations of terms, styles, and proper nouns must be consistent with those given in the background information.

The commit message convention follows the [Conventional Commits](https://www.conventionalcommits.org/) standard.

To ensure that commit messages follow this convention, it is also recommended to install **Commitizen**, which will guide you in writing commit messages that comply with the standard.

> **[Install Commitizen](https://commitizen-tools.github.io/commitizen/#installation)** (recommended)

## <img src="docs/nodejs-icon-alt.svg" height="20" /> Node.js (using nvm)

It is recommended to use **nvm** to install and manage the Node.js version.

> **[Install nvm](https://github.com/nvm-sh/nvm)**

Once nvm is installed, one can install and use the correct version of Node.js:

```bash
nvm install 24.8

nvm use 24.8

# (Recommended: to use version 24.8 as the default)
nvm alias default 24.8
```

## <img src="docs/pnpm.svg" height="20" /> pnpm

The project uses **pnpm** for dependency management.

The recommended method for installing pnpm locally is as follows:

```bash
npm install -g pnpm
```

Make sure to use version 11 (or higher) with:

```bash
pnpm -v
# Should display 11.x.x
```

## <img src="docs/docker-icon.svg" height="20" /> Docker

Although it is possible to manually install the backend and all other services on your own machine, it is recommended to use Docker for faster startup.

> **[Install Docker Desktop](https://www.docker.com/products/docker-desktop/)**

# Installation Requirements

# Installing the project

Start by cloning the project:

> You will need an SSH key to clone the project. Refer to [GitHub’s documentation](https://docs.github.com/fr/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account) to follow the process.

```bash
git clone git@github.com:pass-culture/pass-culture-main.git

cd pass-culture-main
```

Most backend services are managed by automated scripts available in a script named `pc` (for _pass culture_).

To access these scripts, it is recommended to create a symbolic link to the `pc` script at the root of the project:

```bash
./pc symlink
```

Next, install the local environment (Docker Desktop must be running):

```bash
pc install
```

Once the environment is installed, start the backend using the following command at the project root:

```bash
pc start-backend

# or if you have configured the proxy:
pc start-proxy-backend

# ⚠️ This may take several minutes...
```

This will build and start the Docker containers that run the necessary services, including:

- The backend API (accessible on port [:5001](http://localhost:5001))  
- The database (accessible on port **:5434**)  
- The back-office (accessible on port [:5002](http://localhost:5002))

> [!TIP]
>
> If you later want to restart the backend without rebuilding the Docker images, you can use the `--fast` flag:
>
> `pc start-backend --fast` or `pc start-proxy-backend --fast`

## Starting the Front-End

The front-end is located in the `/pro` subfolder, which contains a React application structure.

Normally, the dependencies have already been installed using the `pc` script; otherwise, you can do it manually with `pnpm install`.

To start the front-end application, simply navigate to the `/pro` subfolder and run the command `pnpm start`:

```bash
cd pro

pnpm start
```

A window opens on port [:3001](http://localhost:3001) and displays a login page.

## Sandbox

To generate local data (user accounts, structures, etc.), you can use the `pc sandbox` script:

```bash
pc sandbox -n industrial

# ⚠️ This may take several minutes...
```

Once the data is generated, you can log in to the pro portal using an example account such as:

- Email address: `retention_structures@example.com`
- Password: `user@AZERTY123`

# Development

# Developing

Tips and recommendations for developing on the project.

## Configuring the Editor

The recommended code editor is **VSCode**.

> **[Install VSCode](https://code.visualstudio.com/)**

> [!TIP]
>
> For the Front-End part, it is recommended to open the project **directly at the root of the `/pro` subfolder**.

**Recommended Extensions:**

When you open the project in /pro, VSCode will offer to automatically install the recommended extensions.

The list is available in the file [`.vscode/extensions.json`](https://github.com/pass-culture/pass-culture-main/blob/master/pro/.vscode/extensions.json).

For developers **who do NOT use VSCode** and open the project from the root `pass-culture-main` folder in their IDE:

- [Biome](https://biomejs.dev/guides/getting-started/) (Linter for JS/JSON/CSS/HTML in the Frontend)  
  - `npm i -g @biomejs/biome` or `brew install biome`  
  - Install the [corresponding extension for your IDE if available](https://biomejs.dev/guides/editors/first-party-extensions/)  
  - Make sure your global Biome version matches the one specified in the `dev-deps` of `pro/package.json`.

## Tests

This time, you need to install the `vitest.explorer` extension. Once installed, you’ll be able to access the tests for `*.spec.tsx` files in the Testing tab.

You can also use the launch command `Debug current spec test file`. When inside a `*.spec.tsx` file, you can run this command from the `Run and Debug` tab, and the tests for that file will be executed.

**Unit/Integration Tests:**

The test files are located next to each component or TypeScript file and end with `.spec.ts(x)`.

To run them, use the following command:

```bash
pnpm test:unit

# Run "vitest" with the correct configuration
```

# End-to-End Tests:

We use **Playwright** for the E2E tests. They are available in the subfolder `/pro/e2e`.

More information on E2E tests [here](./e2e/README.md)

## Storybook

The Pro application’s interface components are grouped in an online **Storybook**.

- 🔗 [Online Storybook](https://pass-culture.github.io/pass-culture-main/)

It is also possible to launch Storybook locally using the following command:

```bash
pnpm storybook

# Runs on port:6006
```

## Adage

We integrate a sub-route of the Pro portal (`/adage-iframe/`) into an iframe within ADAGE, the platform for educational institutions to manage their cultural activities.

It is a web application for school project organizers, allowing them to reserve Pass Culture offers for their students.

### Accessing the ADAGE iframe

```bash
# Open the bash console
pc bash

# Generate a token
flask generate_fake_adage_token
```

Simply follow the generated URL to access the app.

### Displaying Offers Locally

Since the local environment is connected to the testing Algolia instance, the IDs returned from Algolia are those from testing, and it’s not guaranteed that the same IDs will be available locally.

To retrieve the IDs of certain offers locally, we can use a local index. To do this, you need to:

- Create a new index in the Algolia sandbox: `<votre_nom>-collective-offers`

- Create a `.env.development.local` file in the `pro/src` directory and set the index name in the `VITE_ALGOLIA_COLLECTIVE_OFFERS_INDEX` variable.

- Create a `.env.local.secret` file in the `api` directory and set the following variables:

```
ALGOLIA_COLLECTIVE_OFFER_TEMPLATES_INDEX_NAME=<your_name>-collective-offers
ALGOLIA_TRIGGER_INDEXATION=1
ALGOLIA_API_KEY=<request the API key>
ALGOLIA_APPLICATION_ID=testingHXXTDUE7H0
SEARCH_BACKEND=pcapi.core.search.backends.algolia.AlgoliaBackend
```

- Open the bash console

pc bash

- Reindex your collective offers

flask reindex_all_collective_offers

## Code and Architecture Standards

Documentation is integrated into the project through README files located at the root of the main directories.

You can find general documentation as well as links to the various README files by following this link:

- 🔗 [Code and Architecture Standards](./src/README.md)

## Technical Debt

We use **SonarCloud** to monitor technical debt.

- 🔗 [Link to the Pro Portal project on SonarCloud](https://sonarcloud.io/project/overview?id=pass-culture_pass-culture-main)

# Strict Constraints
1. **Structure Locking**: Maintain the original Markdown data structure, indentation, heading levels, tables, links, URLs, badges, code blocks, and inline codes exactly as they are.
2. **Selective Translation**: Only translate the visible natural language content intended for users.
3. **Prohibition of Modifications**: It is **strictly forbidden** to translate or alter code tags, key names, variable placeholders (such as {{var}}, ${var}, %s, %d, etc.), command examples, file paths, project names, API names, package names, model names, identifiers, and code symbols; unless a corresponding translation is provided in the background information.
4. The translations of terms, styles, and proper nouns must be consistent with those given in the background information.

# Appendices

You will find useful development scripts in the file [`pro/package.json`](https://github.com/pass-culture/pass-culture-main/blob/master/pro/package.json).

## Generating React component and utility templates with [Templatron](https://www.npmjs.com/package/templatron)

List the available templates:

```bash
npx templatron --list
```

Create a new React component:

```bash
npx templatron component MyNewComponent
```

Create a utility file (e.g., JS function/class):

```bash
npx templatron util MaFonction
```

> [!NOTE]
>
> The template files can be found in the `[`.templatron/`]` directory (`./.templatron/`).

For more details on how the templates work, see the [Templatron documentation](https://github.com/jmpp/templatron).

## Linting TypeScript files

```bash
pnpm lint:js
```

## Identifying Dead Code

```bash
pnpm lint:dead-code
```

## Identifying TS type issues

```bash
pnpm typecheck
```
