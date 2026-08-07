# 🚀 pass Culture PRO — アプリケーションのフロントエンド

<!-- hy-mt2-i18n:start -->
[Español](./README.md) | [中文](./README_zh-CN.md) | [English](./README_en.md) | **日本語**
<!-- hy-mt2-i18n:end -->


この `/pro` ディレクトリには、pass CultureプロフェッショナルポータルのWebアプリケーションに関するすべての設定ファイルとソースコードが含まれています。

**目次**

# 前提条件
## <img src="docs/microsoft-windows-icon.svg" height="20" /> <img src="docs/linux-tux.svg" height="20" /> WSL 2（Windowsのみ）

Windowsを使用するユーザーは、プロジェクトの開発にあたり、Linuxディストリビューション（例：Ubuntu）を搭載した[WSL 2](https://learn.microsoft.com/en-us/windows/wsl/install)の利用を推奨します。

# 厳格な制約事項
1. **構造の維持**：元の Markdown のデータ構造、インデント、見出し階層、表、リンク、URL、バッジ、コードブロック、およびインラインコードを一切変更しないこと。
2. **選択的翻訳**：ユーザーに表示される可視的な自然言語コンテンツのみを翻訳すること。
3. **変更禁止**：コードのタグ、キー名、変数プレースホルダー（{{var}}、${var}、%s、%d など）、コマンド例、ファイルパス、プロジェクト名、API名、パッケージ名、モデル名、識別子、コード記号の翻訳や変更は**厳禁**である。背景情報に対応する翻訳が既に記載されている場合を除く。
4. 用語、スタイル、固有名詞の翻訳は、与えられた背景情報と一致させること。

# 前提条件

## <img src="docs/microsoft-windows-icon.svg" height="20" /> <img src="docs/linux-tux.svg" height="20" /> WSL 2（Windowsのみ）

Windowsをご利用の方は、プロジェクトの開発にあたり、Linuxディストリビューション（例：Ubuntu）を搭載した[WSL 2](https://learn.microsoft.com/en-us/windows/wsl/install)の使用を推奨します。

> **[WSL 2をインストールする](https://learn.microsoft.com/fr-fr/windows/wsl/install)**

## <img src="docs/git-icon.svg" height="20" /> Git

> **[Gitのインストール](https://git-scm.com/downloads)**

このリポジトリでは、以下の設定を使用することが推奨されます：

```bash
# デフォルトのブランチ名を設定する
git config --global init.defaultBranch master

# デフォルトのpullモードを“rebase”に設定する
git config --global pull.rebase true
```

コミットメッセージの規約は、[Conventional Commits](https://www.conventionalcommits.org/)という基準に従っています。

コミットメッセージがこの規約を遵守しているかを確認するために、規約に沿ったコミットメッセージの作成をサポートしてくれる**Commitizen**のインストールも推奨されます。

> **[Commitizenのインストール](https://commitizen-tools.github.io/commitizen/#installation)**（推奨）

## <img src="docs/nodejs-icon-alt.svg" height="20" /> nvm 経由での Node.js

Node.jsのバージョンをインストールおよび管理するには、**nvm**の使用が推奨されます。

> **[nvmのインストール](https://github.com/nvm-sh/nvm)**

nvmをインストールしたら、適切なバージョンのNode.jsをインストールして使用できます：

```bash
nvm install 24.8

nvm use 24.8

# （推奨：デフォルトで24.8バージョンを使用する場合）
nvm alias default 24.8
```

## <img src="docs/pnpm.svg" height="20" /> pnpm

このプロジェクトでは依存関係の管理に**pnpm**を使用しています。

ローカルにpnpmをインストールするための推奨される方法は次のとおりです：

```bash
npm install -g pnpm
```

その後、以下のコマンドを使用してバージョン11以上を利用していることを確認してください：

```bash
pnpm -v
# 11.x.x が表示されるはずです
```

## <img src="docs/docker-icon.svg" height="20" /> Docker

バックエンドやその他のサービスを自分のマシンに手動でインストールすることも可能ですが、より迅速に起動させるためにはDockerを使用することを推奨します。

> **[Docker Desktopのインストール](https://www.docker.com/products/docker-desktop/)**

---

# プロジェクトのインストール

まずはプロジェクトをクローンします：

> プロジェクトをクローンするにはSSHキーが必要です。手順については、[GitHubのドキュメント](https://docs.github.com/ja/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)を参照してください。

```bash
git clone git@github.com:pass-culture/pass-culture-main.git

cd pass-culture-main
```

ほとんдのバックエンドサービスは、`pc`（_pass culture_の略）というスクリプトに用意されている自動化スクリプトによって管理されています。

これらのスクリプトにアクセスするために、プロジェクトのルートにある`pc`スクリプトへのシンボリックリンクを作成することを推奨します：

```bash
./pc symlink
```

次にローカル環境をインストールします（Docker Desktopが起動している必要があります）：

```bash
pc install
```

環境のインストールが完了したら、プロジェクトのルートで以下のコマンドを実行してバックエンドを起動します：

```bash
pc start-backend

# プロキシを設定している場合は：
pc start-proxy-backend

# ⚠️ 実行には数分かかることがあります …
```

これにより、必要なサービスを動作させるためのDockerコンテナがビルドされ、起動されます。具体的には以下のものです：

- バックエンドAPI（ポート[:5001](http://localhost:5001)で応答）
- データベース（ポート**:5434**で応答）
- バックオフィス（ポート[:5002](http://localhost:5002)で応答）

> [!TIP]
>
> 後でDockerイメージを再ビルドせずにバックエンドを再起動したい場合は、`--fast`フラグを使用できます：
>
> `pc start-backend --fast` または `pc start-proxy-backend --fast`

## フロントエンドの起動

フロントエンドは `/pro` というサブディレクトリにあり、そこには React アプリケーションの構造が含まれています。

通常、依存関係は既に `pc` スクリプトによってインストールされていますが、そうでない場合は `pnpm install` を使って手動でインストールできます。

フロントエンドアプリケーションを起動するには、/proというサブディレクトリに移動し、`pnpm start`コマンドを実行するだけです：

```bash
cd pro

pnpm start
```

ポート[:3001](http://localhost:3001)でウィンドウが開き、ログインページが表示されます。

## Sandbox環境

ローカルデータ（ユーザーアカウント、構造体など）を生成するには、`pc sandbox` スクリプトを使用できます：

```bash
pc sandbox -n industrial

# ⚠️ 数分かかる場合があります……
```

データが生成されたら、次のようなサンプルアカウントを使ってproポータルにログインできます：

- メールアドレス：`retention_structures@example.com`  
- パスワード：`user@AZERTY123`

# 厳格な制約
1. **構造の維持**：元のMarkdownのデータ構造、インデント、見出し階層、表、リンク、URL、バッジ、コードブロック、およびインラインコードを一切変更しないこと。
2. **選択的翻訳**：ユーザーが閲覧する可視的な自然言語の内容のみを翻訳すること。
3. **変更禁止**：コードのタグ、キー名、変数プレースホルダー（{{var}}、${var}、%s、%dなど）、コマンド例、ファイルパス、プロジェクト名、API名、パッケージ名、モデル名、識別子、コード記号を翻訳したり変更したりすることは**厳禁**である。背景情報に対応する翻訳名が既に記載されている場合を除く。
4. 用語、スタイル、固有名詞の翻訳は、提供された背景情報と一致させること。

# 開発する

プロジェクトでの開発に関するヒントと推奨事項。

## エディタの設定

推奨されるコードエディタは**VSCode**です。

> **[VSCodeのインストール](https://code.visualstudio.com/)**

> [!TIP]
>
> フロントエンド部分では、プロジェクトを**/proというサブディレクトリのルート直下で開く**ことが推奨されます。

**推奨エクステンション：**

/pro内でプロジェクトを開くと、VSCodeは自動的に推奨される拡張機能のインストールを提案します。

この一覧は、ファイル `[`.vscode/extensions.json`](https://github.com/pass-culture/pass-culture-main/blob/master/pro/.vscode/extensions.json) に記載されています。

VSCodeを使用せず、IDE内の`pass-culture-main`というルートディレクトリからプロジェクトを開く開発者の方へ：

# Biomeの設定
- [Biome](https://biomejs.dev/guides/getting-started/)（フロントエンド向けのJS/JSON/CSS/HTMLリンター）
  - `npm i -g @biomejs/biome` または `brew install biome`
  - IDEに対応する[拡張機能がある場合はそれをインストールする](https://biomejs.dev/guides/editors/first-party-extensions/)
  - グローバルなBiomeのバージョンが `pro/package.json` 内のdev-depsで指定されているものと同じであることに注意する。

## テスト

今回は `vitest.explorer` 拡張機能をインストールする必要があります。そうすれば、Testingタブから `*.spec.tsx` ファイルのテストにアクセスできるようになります。

`Debug current spec test file` という起動コマンドを使用することもできます。`*.spec.tsx` ファイル内にいる場合、`Run and Debug` タブからこのコマンドを実行すると、そのファイルのテストが実行されます。

**単体テスト／統合テスト：**

テストファイルは各コンポーネントやTypeScriptファイルの隣に存在し、拡張子は`.spec.ts(x)`となっています。

これらを実行するには、次のコマンドを使用します：

```bash
pnpm test:unit

# 適切な設定で "vitest" を実行する
```

# E2Eテスト：

E2Eテストには**Playwright**を使用しています。これらのテストファイルは `/pro/e2e` というサブディレクトリにあります。

E2Eテストの詳細については、[こちら](./e2e/README.md)をご覧ください。

## Storybook

Proアプリケーションのインターフェースコンポーネントは、オンラインでアクセス可能な**Storybook**にまとめられています。

- 🔗 [オンラインのStorybook](https://pass-culture.github.io/pass-culture-main/)

以下のコマンドを使用して、ローカルでStorybookを起動することも可能です：

```bash
pnpm storybook

# ポート6006で応答します
```

## Adage

Proポータルのサブルート（`/adage-iframe/`）を、学校の文化活動を管理するためのプラットフォームであるADAGE内のiframeに統合しています。

これは学校のプロジェクトを担当する担当者向けのウェブアプリケーションで、生徒たちのために「Pass Culture」のサービスを予約する機能を提供します。

### ADAGE iframeへのアクセス

```bash
# bashコンソールを開く
pc bash

# トークンを生成する
flask generate_fake_adage_token
```

その後、生成されたURLにアクセスしてアプリに入るだけです。

### ローカル環境でのオファー表示

ローカル環境はテスト用のAlgoliaに接続されているため、Algoliaから返されるIDはテスト用のものとなり、ローカル側で同じIDが得られる保証はありません。

ローカル環境で特定のオファーのIDを取得するには、ローカルインデックスを利用できます。そのためには、以下の手順が必要です：

- Algoliaのサンドボックス上に新しいインデックスを作成する：`<votre_nom>-collective-offers`

- `pro/src` ディレクトリに `.env.development.local` ファイルを作成し、`VITE_ALGOLIA_COLLECTIVE_OFFERS_INDEX` 変数にインデックス名を設定します。

- `api` ディレクトリに `.env.local.secret` ファイルを作成し、以下の変数を設定します：

```
ALGOLIA_COLLECTIVE_OFFER_TEMPLATES_INDEX_NAME=<votre_nom>-collective-offers
ALGOLIA_TRIGGER_INDEXATION=1
ALGOLIA_API_KEY=<apiキーを申請してください>
ALGOLIA_APPLICATION_ID=testingHXXTDUE7H0
SEARCH_BACKEND=pcapi.core.search.backends.algolia.AlgoliaBackend
```

- bashコンソールを開く

```
pc bash
```

- コレクティブオファーの再インデックス作成

```
flask reindex_all_collective_offers
```

## コードおよびアーキテクチャの基準

ドキュメントは、各主要ディレクトリのルートにあるREADMEファイルを通じてプロジェクトに組み込まれています。

このリンクから、一般的なドキュメントや各主要ディレクトリにあるREADMEへのリンクを確認できます：

- 🔗 [コードおよびアーキテクチャの基準](./src/README.md)

## 技術的負債

技術的負債の監視には**SonarCloud**を利用しています。

- 🔗 [SonarCloud上のPortail Proプロジェクトへのリンク](https://sonarcloud.io/project/overview?id=pass-culture_pass-culture-main)

# 厳格な制約事項

# 付録

`[pro/package.json]`ファイル（https://github.com/pass-culture/pass-culture-main/blob/master/pro/package.json）には、開発に役立つスクリプトが記載されています。

## [Templatron](https://www.npmjs.com/package/templatron) を使ってReactコンポーネントおよびユーティリティのテンプレートを生成する

利用可能なテンプレートの一覧を表示する：

```bash
npx templatron --list
```

新しいReactコンポーネントを作成する：

```bash
npx templatron component 新しいReactコンポーネント
```

ユーティリティファイルを作成する（例: JSの関数/クラス）：

```bash
npx templatron util maFonction
```

> [!NOTE]
>
> テンプレートファイルは [`.templatron/` フォルダ](./.templatron/) 内で確認できます。

テンプレートの動作に関する詳細は、[Templatronのドキュメント](https://github.com/jmpp/templatron)をご覧ください。

## TypeScriptファイルのリンタリング

```bash
pnpm lint:js
```

## デッドコードの検出

```bash
pnpm lint:dead-code
```

## TSの型に関する問題を検出する

```bash
pnpm typecheck
```
