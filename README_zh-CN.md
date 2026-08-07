<!-- hy-mt2-i18n:start -->
[Español](./README.md) | **中文** | [English](./README_en.md) | [日本語](./README_ja.md)
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

`main` 仓库包含以下 4 个项目：

- 后端：[api](./api)（Flask）
- 合作伙伴专区：[pro](./pro)（React）
- 面向Pass Culture技术合作伙伴的公共API文档：[doc](./api/documentation)
- 维护页面（HTML）：[maintenance-site](./maintenance-site)

## 安装

### 安装前端与后端共用的依赖项

- [safe-chain](https://www.npmjs.com/package/@aikidosec/safe-chain) # 待办：测试使用 safe-chain 的安装情况
  - `npm i -g @aikidosec/safe-chain`
  - `safe-chain setup`
  - 重启终端

- [Commitizen](https://commitizen-tools.github.io/commitizen/#installation)（用于按规范编写提交信息的 CLI 工具）
  - `brew install commitizen`

- [gitleaks](https://github.com/gitleaks/gitleaks)
  - `brew install gitleaks`

- [semgrep](https://semgrep.dev/)
  - `brew install semgrep`

### 安装所有项目

您需要在 GitHub 账户中拥有 SSH 密钥，才能克隆该仓库。

1. `git clone git@github.com:pass-culture/pass-culture-main.git pass-culture-main`
2. `cd pass-culture-main`
3. `sudo./pc symlink`
4. `pc install`

各个子项目的 README 文件将详细介绍其特定的安装方法。

- [README.md api](./api#readme)
- [README.md pro](./pro#readme)

### 通过 `pc` 脚本启动应用程序

建议阅读上文中关于服务器安装与启动的README说明。不过，如果您时间紧迫，以下是通过调用docker compose的`pc`脚本来启动API及各类前端应用的简短指南。

`pc` 脚本并非该项目的必需组件，始终可以直接使用 `python` 或 `pnpm` 命令来启动服务器。

#### 后端 API

通过 Docker 和 `pc` 脚本：

- [docker](https://docs.docker.com/install/)（已使用 19.03.12 版本测试）
- [docker compose（随 Docker Desktop 一同提供）](https://docs.docker.com/compose/install/#install-compose)（已使用 1.26.2 版本测试）

- `pc start-backend` 或 `pc start-backend --fast` 或 `pc start-proxy-backend` 或 `pc start-proxy-backend --fast`
- `pc sandbox -n industrial`（用于向数据库插入数据）

后端可通过 [http://localhost:5001/](http://localhost:5001/) 访问，也可通过接口 [http://localhost:5001/health/api](http://localhost:5001/health/api) 来测试其功能。

通过 Docker 的一个显著缺点就是延迟以及镜像构建所需的时间。在 `api` 项目的[README](./api#readme)中还有其他启动后端的方法可供参考。

#### 后台管理界面

- 在执行 `pc start-backend` 且 `api` 已开始响应后，[http://localhost:5002/](http://localhost:5002/) 应该已启动并可以正常使用。
- 点击“通过 Google 登录”。
- 接着您将以拥有所有权限的管理员用户 `admin@passculture.local` 身份进入后台管理页面。
- 如果您需要为本地管理员指定特定的电子邮件地址，例如用于连接外部服务，请在 `.env.local.secret` 文件中的 `BACKOFFICE_LOCAL_USER_EMAIL` 变量中填写该地址。

#### Pro端口网站

- `pc start-pro`
- [http://localhost:3001/](http://localhost:3001/) 应已启动并可以正常使用
- 使用 `pctest.admin93.0@example.com`（管理员账号）或 `pctest.pro93.0@example.com`（非管理员账号）进行登录

开发环境中的沙箱用户密码为：`user@AZERTY123`

部署在云端的测试环境（_testing_）出于对测试过程中处理数据的安全保护考虑，使用了密码；而在内部，团队保险箱中保存着“PRO - testing”这一密码。

97版本中也存在这些用户，只需将`93`替换为`97`即可。

更多相关信息请参见[Pro项目的README](./pro/README.md)。

### 实用命令

- 重新构建：`pc rebuild-backend`（在不使用缓存的情况下重新构建 Docker 镜像）
- 重启：`pc restart-backend`（清空数据库并重新启动所有容器）
- 恢复：`pc restore-db file.pgdump`（在本地恢复 PostgreSQL 备份文件 file.pgdump）

### 故障排除

如果 `sandbox` 命令返回我无法解决的错误，可以尝试通过 `pc restart-backend` 删除并重新构建其本地数据库。否则：

- 停止正在运行的镜像
- `docker rm -f pc-postgres` <= 删除容器
- `docker volume rm pass-culture-main_postgres_data` <= 删除数据
- `pc start-backend`
- `pc sandbox -n industrial`

## 部署

### 部署到 Testing 环境

`master` 分支会每小时部署到 testing 环境中。

### 部署到预览环境

需要先安装 [github CLI](https://cli.github.com/)。

要在预览环境中进行部署，请使用 `pc deploy-preview` 命令（完整文档见 [pc](./pc) 脚本）。

### 部署到预发布、生产及集成环境

部署是通过 GitHub Actions 执行的（尤其是 `release--build`、`release--deploy.yml`、`release--build.yml`、`release--build-hotfix.yml` 这些动作），相关文档记录在 Notion 中（文章名为 Tag-MES-et-MEP）。

要查看已部署 API 的版本号：

```
https://backend.staging.passculture.team/health/api
https://backend.passculture.app/health/api
```

## 管理 # 待办：将文档迁移到新基础设施

### 连接到某个环境的 PostgreSQL 数据库

```bash
pc -e <testing|staging|production|integration> psql
```

或者

```bash
pc -e <testing|staging|production|integration> pgcli
```

### 连接本地的 PostgreSQL 数据库

```bash
pc -e <testing|staging|production|integration> psql
```

或者

```bash
pc -e <testing|staging|production|integration> pgcli
```

### 通过命令行使用 Python 连接到环境（testing | staging | production | integration）

```bash
pc -e <testing|staging|production|integration> python
```

### 上传文件

也可以将文件上传到临时环境的 `/usr/src/app/myfile.extension` 路径下。

```bash
pc -e <testing|staging|production|integration> -f myfile.extension python
```

```bash
pc -e <testing|staging|production|integration> -f myfile.extension bash
```

### 查看数据库日志

在本地：

```bash
pc access-db-logs
```

在其他环境中：

```bash
pc -e <testing|staging|production> access-db-logs
```
