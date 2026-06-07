# Microforce DB Core

**Microforce DB Core** は、AIエージェントが自律的かつ安全にデータ構造（スキーマ）を定義・拡張し、データの追加・取得を行えるように設計された、自己完結型の SQLite データベースフレームワークおよび MCP（Model Context Protocol）サーバーです。

中小企業向けのオンプレミス（閉域網）完結型システムや、AIエージェントによる自律運用の「核」として、高い信頼性と堅牢性を担保します。

---

## 主な特徴

1. **AST解析によるスキーマ防御（AST Guardrail）**
   AIがスキーマ定義ファイル（`models_ai.py`）を動的に生成・適用する際、Pythonの抽象構文木（AST）を用いて静的解析を行います。
   - `sqlalchemy` および `src.database.models_core` 以外の不要なインポートをブロック。
   - モジュールレベルでの代入式や関数実行など、悪意のある実行コードを完全排除。
   - 既存テーブル・カラムの削除や変更を禁止し、新規テーブルの追加のみを許可する「Plan A（追加のみ）」ルールを強制します。

2. **`asyncio.Queue` による安全な並行書き込み（Concurrency Queue）**
   SQLiteで頻発する「Database is locked」エラーを防ぐため、書き込み・更新タスク（Insert/Update/Delete）を単一のスレッド風キューに集約して直列化。負荷の高い非同期同時アクセスでもデータの喪失や衝突を防ぎます。

3. **動的 Pydantic v2 バリデーション**
   SQLAlchemyのテーブルモデルから、実行時に動的にPydanticバリデーションモデルを生成。データベースへの書き込み前に必須項目の検証やデータ型チェックを厳密に行い、不正データの混入を防止します。

4. **FastMCP インターフェース**
   外部のAIクライアントから即座に操作可能なMCPツールを提供。
   - `insert_record`: キューを経由した安全なレコード追加
   - `get_records`: 柔軟なフィルタリングによるデータ取得
   - `update_schema`: スキーマ（`models_ai.py`）の動的な更新・適用

5. **グレースフル・シャットダウン**
   シャットダウンシグナルを検知すると、キューに残っているすべての書き込みタスクを処理した後に、DB接続を安全にクローズします。

---

## システムアーキテクチャ

```mermaid
graph TD
    subgraph AI Client / MCP Host
        Agent[AI Agent / Beads / Superpowers]
    end

    subgraph Microforce DB Core (MCP Server)
        MCP[FastMCP Server]
        Validator[AST / Pydantic Validator]
        Queue[asyncio.Queue]
        Worker[Queue Worker]
        DB[(SQLite / aiosqlite)]
    end

    Agent -->|1. Tools Call| MCP
    MCP -->|2. Code / Data Validation| Validator
    Validator -->|3. Validated Data| Queue
    Queue -->|4. Pop Task| Worker
    Worker -->|5. Safe Serialized Write| DB
    DB -->|6. Query Result| MCP
    MCP -->|7. Tool Response| Agent
```

---

## 導入方法

### 前提条件
- Python 3.10 以上

### インストール
リポジトリをクローンし、依存パッケージをインストールします。

```bash
# 仮想環境の作成とアクティベート
python -m venv .venv
source .venv/bin/activate  # Windowsの場合は .venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

---

## クイックスタート

### 1. MCPサーバーの起動
FastMCPサーバーを起動します。

```bash
python -m src.mcp.server
```
起動すると、標準入出力（stdio）を介してMCPホストと接続可能な状態になります。

### 2. スキーマの更新（AIによるテーブル定義追加）
MCPツール `update_schema` を呼び出し、新しいスキーマ定義を送信します。

**送信コードの例 (Python)**:
```python
from sqlalchemy import Column, Integer, String
from src.database.models_core import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
```

このコードはASTバリデーターによって検証された後、安全に `src/database/models_ai.py` に書き込まれ、データベースへ即座に反映されます。

### 3. レコードの挿入
スキーマ追加後、`insert_record` ツールを使用してレコードを安全に挿入できます。

**パラメータ例**:
- `class_name`: `"Product"`
- `payload_json`: `'{"name": "Laptop", "price": 120000}'`

動的に生成された Pydantic モデルによって値がバリデーションされた後、キューを経由してデータベースに安全に書き込まれます。

---

## テストの実行

プロジェクトには、信頼性を担保するための包括的なテスト（12ケース）が同梱されています。

```bash
# pytestの実行
pytest -v
```

テスト実行中は自動的に一時データベース（テスト隔離環境）がバインドされるため、開発用・本番用のデータベースに影響を与えることなく検証可能です。

---

## ライセンス

このプロジェクトは [MIT License](LICENSE) のもとで公開されています。
