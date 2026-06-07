# GitHub公開用パッケージングの設計図

このドキュメントは、構築した「セキュアSQLite MCPフレームワーク（Microforce DB Core）」をGitHubの公開リポジトリとして公開するための手順、準備チェックリスト、およびリポジトリ構成を整理した設計図ですわ。

---

## 1. 公開前のチェックリスト（事前準備）

公開前に必ず以下の項目を確認・実行してください。

1. **機密情報の排除**
   - データベースの実データが含まれる `microforce.db` や `.env` ファイルがリポジトリに含まれないよう、`.gitignore` が正しく機能しているか確認してください。
   - APIキー（Gemini APIキーなど）がソースコード内にハードコーディングされていないことを確認してください。
2. **絶対パスの排除**
   - ソースコードおよびテストコード内のパス指定が、すべて相対パスまたは `os.getenv` 等の環境変数経由になっていることを確認してください（検証済み）。
3. **不要なファイルの削除**
   - `__pycache__` や `.pytest_cache`、仮想環境フォルダ（`.venv`）など、Pythonが生成するキャッシュファイルをすべて削除します。
4. **テストの実行**
   - 公開する状態のコードで `pytest` を実行し、すべてのテスト（12件）が正常にパスすることを確認します。

---

## 2. GitHubへの公開手順

初めてGitHubにリポジトリを公開する際のコマンド手順ですわ。

### ステップ 1: ローカルGitリポジトリの初期化
まだローカルでGit管理を行っていない場合、`backend` ディレクトリ直下で以下を実行します。

```bash
# Gitリポジトリの初期化
git init

# デフォルトブランチ名をmainに設定
git checkout -b main
```

### ステップ 2: 必要なファイルのステージングとコミット
公開に必要なコードとドキュメントのみをステージングします。

```bash
# すべてのファイルをステージング（.gitignoreで指定されたファイルは自動で除外されます）
git add .

# コミットの作成
git commit -m "Initial commit: Secure SQLite MCP Framework with Concurrency Queue and AST Safeguards"
```

### ステップ 3: GitHubでのリポジトリ作成
1. [GitHub](https://github.com/) にログインします。
2. 画面右上の「+」アイコンから「**New repository**」を選択します。
3. リポジトリ名（例: `microforce-db-core`）を入力します。
4. 公開範囲を「**Public**」に設定します。
5. *注意*: 「Initialize this repository with:」の項目（README, .gitignore, License）は、すべてチェックを外した状態（空のリポジトリ）にしてください（ローカルで既に作成しているためですわ）。
6. 「**Create repository**」をクリックします。

### ステップ 4: リモートリポジトリの紐付けとプッシュ
GitHubに表示されるコマンドを参考に、リモートリポジトリを追加してプッシュします。

```bash
# リモートリポジトリの登録（<username>と<repo-name>は実際のものに置き換えてください）
git remote add origin git@github.com:<username>/<repo-name>.git

# 初回プッシュ
git push -u origin main
```

---

## 3. リポジトリ構成（公開ファイル一覧）

GitHubに公開される最小構成は以下の通りです。

```text
microforce-db-core/
├── .github/
│   └── workflows/
│       └── test.yml       # GitHub Actions CI設定
├── src/
│   ├── __init__.py
│   ├── main.py            # アプリケーションのエントリーポイント
│   ├── database/
│   │   ├── __init__.py
│   │   ├── crud.py        # 汎用CRUD操作およびPydanticモデル動的生成
│   │   ├── engine.py      # SQLAlchemy 非同期接続エンジン
│   │   ├── models_core.py # 組み込み基本テーブル定義
│   │   ├── models_ai.py   # AIが動的に拡張するスキーマファイル（空または初期状態）
│   │   ├── queue_worker.py# 非同期書き込みシリアライザキュー
│   │   ├── pydantic_validator.py # データバリデーター
│   │   └── schema_validator.py   # ASTセキュリティガードレール
│   └── mcp/
│       ├── __init__.py
│       ├── server.py      # MCPサーバー本体（FastMCP）
│       ├── tools_data.py  # データ操作用MCPツール定義
│       └── tools_schema.py# スキーマ更新用MCPツール定義
├── tests/
│   ├── conftest.py        # テスト用DB隔離・フィクスチャ設定
│   ├── test_concurrency.py# 並行処理/負荷テスト
│   ├── test_schema.py     # 動的スキーマ拡張テスト
│   ├── test_shutdown.py   # グレースフル・シャットダウンテスト
│   ├── test_validation.py # Pydanticデータ検証テスト
│   └── test_validator.py  # ASTガードレールセキュリティテスト
├── .gitignore             # Git管理除外設定
├── LICENSE                # MITライセンスファイル
├── README.md              # プロジェクト説明書
├── pytest.ini             # テスト用初期設定ファイル
└── requirements.txt       # 依存パッケージ定義ファイル
```

---

## 4. 公開後の保守と運用

1. **GitHub Actions のステータス監視**
   - コードを更新して `git push` するたびに、`.github/workflows/test.yml` に定義されたテストが自動実行されます。
   - リポジトリの「Actions」タブからビルド結果を確認できますわ。
2. **Issues と Pull Requests**
   - 利用者からのバグ報告や改善提案を受け付ける窓口になります。必要に応じてテンプレートなどを整備すると、よりOSSらしくなりますわ。
3. **Beadsタスクの更新**
   - プロダクトとしてのマイルストーンや公開後の改善タスクは、Beads（`bd`）を用いて管理し、変更履歴をスマートに残していきましょう。
