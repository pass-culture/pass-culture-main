# 🚀 pass Culture PRO — 前端应用

<!-- hy-mt2-i18n:start -->
[Español](./README.md) | **中文** | [English](./README_en.md) | [日本語](./README_ja.md)
<!-- hy-mt2-i18n:end -->


该 `/pro` 目录包含了 Pass Culture 专业版门户网站的全部配置文件及前端源代码。

**目录**

- [先决条件](#pré-requis)
  - [WSL 2（仅限 Windows）](#--wsl-2-windows-uniquement)
  - [Git](#-git)
  - [Node.js（通过 nvm 安装）](#-nodejs-via-nvm)
  - [pnpm](#-pnpm)
  - [Docker](#-docker)
- [项目安装](#installer-le-projet)
  - [运行前端应用](#lancer-le-front-end)
  - [沙箱环境](#sandbox)
- [开发相关](#développer)
  - [配置编辑器](#configurer-son-éditeur)
  - [测试](#les-tests)
  - [Storybook](#storybook)
  - [Adage](#adage)
  - [代码与架构标准](#standards-de-code-et-darchitecture)
  - [技术债务](#dette-technique)
- [附录](#annexes)

# 严格约束
1. **结构锁定**：绝对保持原有的 Markdown 数据结构、缩进、标题层级、表格、链接、URL、徽章、代码块和行内代码完全不变。
2. **选择性翻译**：仅翻译面向用户展示的可见自然语言内容。
3. **禁止修改**：**严禁**翻译或更改代码标签、键名、变量占位符（如 {{var}}、${var}、%s、%d 等）、命令示例、文件路径、项目名、API 名、包名、模型名、标识符和代码符号；除非背景信息中已经给出对应译名。
4. 术语、风格、专有名词的译法要与所给背景信息保持一致。

# 先决条件

## <img src="docs/microsoft-windows-icon.svg" height="20" /> <img src="docs/linux-tux.svg" height="20" /> WSL 2（仅限 Windows）

对于 Windows 用户，建议使用带有 Linux 发行版（例如 Ubuntu）的[WSL 2](https://learn.microsoft.com/en-us/windows/wsl/install)来开发该项目。

> **[安装 WSL 2](https://learn.microsoft.com/fr-fr/windows/wsl/install)**

## <img src="docs/git-icon.svg" height="20" /> Git 版本控制工具

> **[安装 Git](https://git-scm.com/downloads)**

建议为此仓库使用以下配置：

```bash
# 设置默认分支名称
git config --global init.defaultBranch master

# 将默认的拉取模式设置为“rebase”
git config --global pull.rebase true
```

提交信息规范遵循 [Conventional Commits](https://www.conventionalcommits.org/) 标准。

为确保提交信息遵循该规范，也建议安装 **Commitizen**，它将帮助您撰写符合规范的提交信息。

> **[安装 Commitizen](https://commitizen-tools.github.io/commitizen/#installation)**（推荐）

## <img src="docs/nodejs-icon-alt.svg" height="20" /> 通过 nvm 安装的 Node.js

建议使用 **nvm** 来安装及管理 Node.js 版本。

> **[安装 nvm](https://github.com/nvm-sh/nvm)**

安装完 nvm 后，就可以安装并使用正确版本的 Node.js 了：

```bash
nvm install 24.8

nvm use 24.8

# （建议：将默认版本设置为24.8）
nvm alias default 24.8
```

## <img src="docs/pnpm.svg" height="20" /> pnpm

该项目使用 **pnpm** 来管理依赖项。

在本地安装 pnpm 的推荐方法如下：

```bash
npm install -g pnpm
```

随后请确保使用版本 11（或更高版本），操作方式如下：

```bash
pnpm -v
# 应显示 11.x.x
```

## <img src="docs/docker-icon.svg" height="20" /> Docker

虽然可以在本地手动安装后端及所有其他服务，但建议使用 Docker 以更快地启动它们。

> **[安装 Docker Desktop](https://www.docker.com/products/docker-desktop/)**

# 安装项目

# 安装项目

首先克隆项目：

> 要克隆该项目，您需要一个 SSH 密钥。请参阅 [GitHub 文档](https://docs.github.com/fr/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account) 了解操作步骤。

```bash
git clone git@github.com:pass-culture/pass-culture-main.git

cd pass-culture-main
```

大多数后端服务都由自动化脚本管理，这些脚本位于名为 `pc`（即_pass culture_的缩写）的脚本文件中。

为方便使用这些脚本，建议在项目根目录下为 `pc` 脚本创建一个符号链接：

```bash
./pc symlink
```

接着安装本地环境（需已启动 Docker Desktop）：

```bash
pc install
```

环境安装完成后，在项目根目录中使用以下命令启动后端服务：

```bash
pc start-backend

# 或者，如果您已配置了代理：
pc start-proxy-backend

# ⚠️ 此过程可能需要几分钟时间……
```

这样将会构建并启动用于运行所需服务的 Docker 容器，具体包括：

- 后端 API（监听端口[:5001](http://localhost:5001)）
- 数据库（监听端口**:5434**）
- 后台管理界面（监听端口[:5002](http://localhost:5002)）

> [!提示]
>
> 如果日后您希望在不重新构建 Docker 镜像的情况下重启后端，可以使用 `--fast` 参数：
>
> `pc start-backend --fast` 或 `pc start-proxy-backend --fast`

## 启动前端应用

前端位于 `/pro` 子目录中，该目录内包含一个 React 应用的结构。

通常，依赖项已通过 `pc` 脚本安装完成，否则也可以使用 `pnpm install` 手动安装。

要启动前端应用，只需进入 `/pro` 子目录，然后运行 `pnpm start` 命令即可：

```bash
cd pro

pnpm start
```

一个窗口会在端口[:3001](http://localhost:3001)上打开，并显示登录页面。

## 沙箱模式

若要生成本地数据（如用户账户、结构数据等），可使用 `pc sandbox` 脚本：

```bash
pc sandbox -n industrial

# ⚠️ 可能需要几分钟时间……
```

数据生成后，即可使用如下示例账户登录专业门户：

- 邮箱地址：`retention_structures@example.com`
- 密码：`user@AZERTY123`

# 开发
关于在该项目中开发的建议与指导。

# 开发

关于在该项目中开发的建议与指导。

## 配置编辑器

推荐的代码编辑器是**VSCode**。

> **[安装 VSCode](https://code.visualstudio.com/)**

> [!TIP]
>
> 对于前端部分，建议直接在 `/pro` 子目录的根目录下打开该项目。

**推荐扩展：**

当您在 /pro 目录下打开该项目时，VSCode 会自动提示您安装推荐的扩展程序。

该列表可在文件 `[“.vscode/extensions.json”](https://github.com/pass-culture/pass-culture-main/blob/master/pro/.vscode/extensions.json)` 中查看。

对于那些**不使用 VSCode**、而是在 IDE 中从 `pass-culture-main` 根目录打开该项目的开发者：

# Biome工具（前端JS/JSON/CSS/HTML代码检查工具）
- [Biome](https://biomejs.dev/guides/getting-started/)  
  - `npm i -g @biomejs/biome` 或 `brew install biome`  
  - 安装适用于你所用IDE的[对应扩展（如有）](https://biomejs.dev/guides/editors/first-party-extensions/)  
  - 确保全局安装的Biome版本与 `pro/package.json` 中的dev-deps所指定的版本一致。

## 测试

这次需要安装 `vitest.explorer` 扩展。这样就能在“Testing”选项卡中查看 `*.spec.tsx` 文件的测试结果了。

也可以使用 `Debug current spec test file` 这个启动命令。当处于 `*.spec.tsx` 文件中时，可从“运行与调试”选项卡中执行该命令，即可运行该文件的测试。

**单元测试/集成测试：**

测试文件位于每个组件或 TypeScript 文件的旁边，文件名以 `.spec.ts(x)` 结尾。

要运行它们，可使用以下命令：

```bash
pnpm test:unit

# 以正确的配置运行 "vitest"
```

# 端到端测试：

我们使用 **Playwright** 进行端到端测试。这些测试文件位于 `/pro/e2e` 子目录中。

有关端到端测试的更多信息，请点击[此处](./e2e/README.md)。

## Storybook

Pro 应用的界面组件被汇总在可在线访问的 **Storybook** 中。

- 🔗 [在线 Storybook](https://pass-culture.github.io/pass-culture-main/)

也可以使用以下命令在本地启动 Storybook：

```bash
pnpm storybook

# 在端口 6006 上运行
```

## ADAGE 平台

我们将在 ADAGE 中的 iframe 内嵌入 Pro 平台的一个子路径（`/adage-iframe/`），而 ADAGE 则是供学校管理其文化活动的平台。

这是一个专为学校项目策划人员设计的网页应用，可帮助他们为学生预订“文化通行证”上的各类优惠服务。

### 访问 ADAGE iframe

```bash
# 打开 bash 控制台
pc bash

# 生成令牌
flask generate_fake_adage_token
```

随后只需按照生成的 URL 进入该应用即可。

### 在本地显示优惠信息

由于本地环境连接的是测试用的 Algolia，从 Algolia 返回的 ID 都是测试用的，因此无法保证本地环境中的 ID 与之相同。

要在本地获取某些优惠的ID，可以使用本地索引。为此需要：

- 在 Algolia 测试沙箱中创建一个新的索引：<votre_nom>-collective-offers

- 在 `pro/src` 目录下创建一个 `.env.development.local` 文件，并在 `VITE_ALGOLIA_COLLECTIVE_OFFERS_INDEX` 变量中填写索引名称。

- 在 `api` 目录下创建一个 `.env.local.secret` 文件，并填写以下变量：

```
ALGOLIA_COLLECTIVE_OFFER_TEMPLATES_INDEX_NAME=<votre_nom>-collective-offers
ALGOLIA_TRIGGER_INDEXATION=1
ALGOLIA_API_KEY=<需申请API密钥>
ALGOLIA_APPLICATION_ID=testingHXXTDUE7H0
SEARCH_BACKEND=pcapi.core.search.backends.algolia.AlgoliaBackend
```

- 打开 bash 控制台

pc bash

- 重新索引您的集体优惠商品

flask reindex_all_collective_offers

## 代码与架构标准

文档已通过各主要目录根部的 README 文件集成到项目中。

您可以通过以下链接查看通用文档以及各目录下 README 文件的链接：

- 🔗 [代码与架构标准](./src/README.md)

## 技术债务

我们使用 **SonarCloud** 来监控技术债务。

- 🔗 [SonarCloud 上的 Portail Pro 项目链接](https://sonarcloud.io/project/overview?id=pass-culture_pass-culture-main)

# 严格约束
1. **结构锁定**：绝对保持原有的 Markdown 数据结构、缩进、标题层级、表格、链接、URL、徽章、代码块和行内代码完全不变。
2. **选择性翻译**：仅翻译面向用户展示的可见自然语言内容。
3. **禁止修改**：**严禁**翻译或更改代码标签、键名、变量占位符（如 {{var}}、${var}、%s、%d 等）、命令示例、文件路径、项目名、API 名、包名、模型名、标识符和代码符号；除非背景信息中已经给出对应译名。
4. 术语、风格、专有名词的译法要与所给背景信息保持一致。

# 附录

在文件[`pro/package.json`](https://github.com/pass-culture/pass-culture-main/blob/master/pro/package.json)中，您可以找到有助于开发的实用脚本。

## 使用 [Templatron](https://www.npmjs.com/package/templatron) 生成 React 组件与工具类模板

列出可用的模板：

```bash
npx templatron --list
```

创建一个新的 React 组件：

```bash
npx templatron component 我的新React组件
```

创建工具文件（例如：JS 函数/类）：

```bash
npx templatron util 我的函数
```

> [!NOTE]
>
> 模板文件可在 [`.templatron/` 目录](./.templatron/) 中查看。

如需了解模板功能的更多详情，请参阅 [Templatron 的文档](https://github.com/jmpp/templatron)。

## 对 TypeScript 文件进行代码检查

```bash
pnpm lint:js
```

## 识别死代码

```bash
pnpm lint:dead-code
```

## 检测 TypeScript 类型问题

```bash
pnpm typecheck
```
