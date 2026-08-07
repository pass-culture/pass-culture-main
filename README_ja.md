<!-- hy-mt2-i18n:start -->
[Español](./README.md) | [中文](./README_zh-CN.md) | [English](./README_en.md) | **日本語**
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

repo `main`には、以下の4つのプロジェクトが含まれています：

- バックエンド：[api](./api)（Flask）
- パートナー専用ページ：[pro](./pro)（React）
- Pass Cultureの技術パートナー向け公開APIのドキュメント：[doc](./api/documentation)
- メンテナンスページ（HTML）：[maintenance-site](./maintenance-site)

## インストール

### フロントエンドとバックエンドで共通に使用される依存関係のインストール

- [safe-chain](https://www.npmjs.com/package/@aikidosec/safe-chain) # TODO: safe-chainを使ったインストールテストを実施する
  - `npm i -g @aikidosec/safe-chain`
  - `safe-chain setup`
  - ターミナルを再起動する

- [Commitizen](https://commitizen-tools.github.io/commitizen/#installation)（適切な形式でコミットを記述するためのCLIツール）
  - `brew install commitizen`

- [gitleaks](https://github.com/gitleaks/gitleaks)
  - `brew install gitleaks`

- [semgrep](https://semgrep.dev/)
  - `brew install semgrep`

### 全てのプロジェクトをインストールする

リポジトリをクローンするには、GitHub プロフィールにSSHキーを持っている必要があります。

1. `git clone git@github.com:pass-culture/pass-culture-main.git pass-culture-main`
2. `cd pass-culture-main`
3. `sudo./pc symlink`
4. `pc install`

各サブプロジェクトのREADMEには、それぞれの特定のインストール方法が詳しく記載されています。

- [README.md api](./api#readme)
- [README.md pro](./pro#readme)

### スクリプト `pc` を使ってアプリケーションを起動する

サーバーのインストールおよび起動については、上記の段落にあるREADMEをご覧になることを推奨します。ただし、時間に余裕がない場合は、docker composeを利用するスクリプト`pc`を使ってAPIや各フロントエンドを起動するための簡単な手順を以下に示します。

スクリプト `pc` はこのプロジェクトに必須なものではなく、`python` や `pnpm` といったコマンドを直接使用してサーバーを起動することも常に可能です。

#### バックエンド API

Dockerおよび`pc`スクリプトを使用して：

- [docker](https://docs.docker.com/install/) (19.03.12でテスト済み)  
- [docker compose (Docker Desktopに含まれている)](https://docs.docker.com/compose/install/#install-compose) (1.26.2でテスト済み)

- `pc start-backend` または `pc start-backend --fast` または `pc start-proxy-backend` または `pc start-proxy-backend --fast`
- `pc sandbox -n industrial`（DBにデータを挿入するため）

バックエンドは [http://localhost:5001/](http://localhost:5001/) からアクセスでき、[http://localhost:5001/health/api](http://localhost:5001/health/api) というエンドポイントを通じてその動作をテストすることが可能です。

Dockerを利用する場合の大きな欠点は、レイテンシーやイメージの作成にかかる時間です。`api`の[README](./api#readme)には、バックエンドを起動するその他の方法も記載されています。

#### バックオフィス

- `pc start-backend`を実行し、`api`が応答したら、[http://localhost:5002/](http://localhost:5002/)も起動して動作するはずです。
- _Google経由でログイン_をクリックしてください。
- すると`admin@passculture.local`という管理者ユーザーとして、すべての権限を持ってBOのホームページに移動します。
- 外部サービスとの連携などのためにローカル管理者用の特定のメールアドレスが必要な場合は、`.env.local.secret`ファイル内の`BACKOFFICE_LOCAL_USER_EMAIL`変数にそのメールアドレスを指定してください。

#### Proポータル

- `pc start-pro`
- [http://localhost:3001/](http://localhost:3001/) は起動され、正常に動作しているはずです
- `pctest.admin93.0@example.com`（管理者）または `pctest.pro93.0@example.com`（非管理者）を使ってログインしてください

開発環境におけるサンドボックスユーザーのパスワードは `user@AZERTY123` です。

クラウド上にデプロイされているテスト環境（_testing_）では、テスト時に扱われるデータを保護するために秘密のパスワードが使用されています。社内では、「PRO - testing」というパスワードがチームの金庫に保管されています。

これらのユーザーは97環境にも存在し、`93`を`97`に置き換えるだけです。

その他の詳細については、[ProのREADME](./pro/README.md)をご覧ください。

### 便利なコマンド

- 再構築：`pc rebuild-backend`（キャッシュなしでDockerイメージを再構築）
- 再起動：`pc restart-backend`（データベースを消去し、すべてのコンテナを再起動）
- 復元：`pc restore-db file.pgdump`（ローカルにあるPostgreSQLダンプファイル（file.pgdump）を復元）

### トラブルシューティング

もし `sandbox` コマンドで解決できないエラーが発生した場合は、`pc restart-backend` を使ってローカルのBDDを削除し、再構築してみることができます。それでもダメなら：

- 実行中のコンテナを停止する
- `docker rm -f pc-postgres` <= コンテナの削除
- `docker volume rm pass-culture-main_postgres_data` <= データの削除
- `pc start-backend`
- `pc sandbox -n industrial`

## 部署

### Testing環境へのデプロイ

`master`ブランチは、毎時間テスト環境にデプロイされます。

### プレビュー環境へのデプロイ

[github CLI](https://cli.github.com/) をインストールしておく必要があります。

プレビュー環境にデプロイするには、`pc deploy-preview` コマンドを使用してください（詳細なドキュメントはスクリプト [pc](./pc) にあります）。

### Staging、Production、Integration環境へのデプロイ

デプロイはGitHubのアクション（特に`release--build`、`release--deploy.yml`、`release--build.yml`、`release--build-hotfix.yml`）を通じて行われ、Notionに記事「Tag-MES-et-MEP」として記録されています。

デプロイされたAPIのバージョン番号を確認するには：

```
https://backend.staging.passculture.team/health/api
https://backend.passculture.app/health/api
```

## 管理 # TODO: ドキュメントを新しいインフラストラクチャに移行する

### 環境のPostgreSQLデータベースへの接続

```bash
pc -e <testing|staging|production|integration> psql
```

または

```bash
pc -e <testing|staging|production|integration> pgcli
```

### ローカルのPostgreSQLデータベースへの接続

```bash
pc -e testing psql
```

または

```bash
pc -e <testing|staging|production|integration> pgcli
```

### 環境（testing | staging | production | integration）へのpythonコマンドライン経由での接続

```bash
pc -e <testing|staging|production|integration> python
```

### ファイルのアップロード

一時環境内の `/usr/src/app/myfile.extension` という場所にファイルをアップロードすることも可能です。

```bash
pc -e <testing|staging|production|integration> -f myfile.extension python
```

```bash
pc -e <testing|staging|production|integration> -f myfile.extension bash
```

### データベースのログにアクセスする

ローカル環境では：

```bash
pc access-db-logs
```

その他の環境では：

```bash
pc -e <testing|staging|production> access-db-logs
```
