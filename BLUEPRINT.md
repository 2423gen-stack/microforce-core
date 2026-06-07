# Microforce Architectural Blueprint / (マイクロフォース) アーキテクチャ設計図

*Read this in other languages: [English](#english), [日本語](#japanese)*

---

<a id="english"></a>
## [English] Microforce Architectural Blueprint

### 1. Project Overview and Vision

#### Concept
"An AI-powered, ultra-lightweight database foundation that is affordable, easy to implement, and tailored to the actual needs of small and medium-sized enterprises (SMEs), without relying on expensive and complex systems."

#### Architectural Goals (The Endgame)
*   **Maintenance-Free:** Eliminates the operational burden of traditional RDBMS. Achieves robust operation while remaining a "local-complete" system using single-file SQLite.
*   **Foundation for Autonomous Expansion:** Designed to integrate task management and powerful AI agent extension environments, encapsulating the entire system.
*   **AI-Driven Backend:** By passing specifications to external AI via MCP (Model Context Protocol), it establishes a "fully autonomous backend" where external AI can autonomously execute feature additions (including schema changes) and data I/O without hesitation.

---

### 2. Core Technology Stack

This foundation is composed of the following stack to balance robustness with ease of implementation:

1.  **Database:** `SQLite`
    *   Local-complete, single-file configuration. Extremely easy to backup and migrate, optimized for environments without dedicated infrastructure personnel.
2.  **ORM Layer:** `Python` + `SQLAlchemy`
    *   Implements and processes type specifications using object-oriented logic as in-class properties, rather than relying on raw SQL definitions.
3.  **Asynchronous Message Queue (Serialization Buffer Layer):**
    *   Adopts an asynchronous queue such as `asyncio.Queue`.
    *   To avoid SQLite's specific "lock contention issues during concurrent writes", requests are serialized and poured into the DB. Achieves safe, high-concurrency processing without depending on heavy external middleware (like Redis or RabbitMQ).
4.  **AST-Based Static Analysis & Schema Protection (`schema_validator.py`):**
    *   Introduces an analysis mechanism using Python's Abstract Syntax Tree (AST) to safely handle dynamic schema changes (adding tables, columns, etc.) via AI interfaces.
    *   Functions as a "checkpoint" to ensure the safety of AI autonomous expansion by enforcing "Append-only" rules to prevent destruction of existing models and proactively filtering out malicious code execution, such as unauthorized module imports.

---

### 3. Quality Assurance (QA) and Testing Strategy

To prove the robustness of the system, the following tests have been implemented and passed against the core functions of the foundation:

1.  **Concurrency Load Test:**
    *   Verified that when a massive amount of asynchronous INSERT/UPDATE requests are simultaneously sent from pseudo-multi-clients, the message queue completely prevents lock contention, and data is processed sequentially without loss.
2.  **Type Safety & Schema Validation Test:**
    *   Confirmed that intentional injection of incorrect data types (e.g., numbers into string columns) is blocked at the SQLAlchemy layer.
    *   Verified through AST analysis tests that unauthorized code and destructive changes that do not meet security requirements are correctly rejected during schema file modifications.

*Note: This repository pre-releases the "core" part of this robust backend foundation.*

---

<br>

<a id="japanese"></a>
## [日本語] Microforce (マイクロフォース) アーキテクチャ設計図

### 1. プロジェクト概要とビジョン

#### コンセプト
「高価で複雑なシステムに依存せず、中小企業の実態に即した安価で導入・実装が容易なAI搭載型・超軽量データベース基盤」

#### アーキテクチャの目的 (The Endgame)
*   **メンテナンスフリー:** RDBMSの運用負荷を排除し、単一ファイルのSQLiteによる「ローカル完結型」でありながら堅牢な運用を実現する。
*   **自律拡張の基盤:** 今後、タスク管理や強力なAIエージェント拡張環境を統合し、システム全体をカプセル化する。
*   **AI駆動型バックエンド:** 仕様をMCP経由で外部AIに渡すことで、外部AIが「一切迷うことなく」自律的に機能追加（スキーマ変更含む）やデータI/Oを実行できる「完全自律バックエンド」を確立する。

---

### 2. コア・テクノロジースタック

本基盤は、堅牢性と実装の容易さを両立させるため、以下のスタックで構成されています。

1.  **データベース:** `SQLite`
    *   ローカル完結、単一ファイル構成。バックアップや移行が極めて容易であり、インフラ専任者がいない環境に最適化。
2.  **ORMレイヤー:** `Python` + `SQLAlchemy`
    *   型指定をSQLの生定義に依存するのではなく、クラス内プロパティとしてオブジェクト指向のロジックで実装・処理。
3.  **非同期メッセージキュー（直列化バッファ層）:**
    *   `asyncio.Queue` 等を用いた非同期キューを採用。
    *   SQLite特有の「同時書き込み時のロック競合問題」を回避するため、リクエストを直列化してDBへ流し込む。外部の重厚なミドルウェア（RedisやRabbitMQなど）に依存することなく、高並行処理を安全に実現。
4.  **ASTベースの静的解析・スキーマ保護機能 (`schema_validator.py`):**
    *   AIインターフェース経由でのスキーマの動的変更（テーブル追加、カラム追加など）を安全に行うため、Pythonの抽象構文木（AST）を用いた解析機構を導入。
    *   既存モデルの破壊を防ぐための「追記型（Append-only）ルールの強制」や、許可されないモジュールのインポートなど不正なコードの実行を事前検証で排除し、AIによる自律拡張の安全性を担保する「関所」として機能。

---

### 3. 品質保証（QA）とテスト戦略

システムの堅牢性を証明するため、基盤のコア機能に対して以下のテストが実施・パスしています。

1.  **並行書き込み負荷テスト (Concurrency Test):**
    *   疑似的なマルチクライアントから非同期で大量のINSERT/UPDATEリクエストを同時に送信し、メッセージキューがロック競合を完全に防ぎ、データが欠損なくシーケンシャルに処理されることを検証。
2.  **型安全・スキーマ検証テスト (Type & Schema Validation):**
    *   意図的に間違ったデータ型（文字列カラムに数値など）の注入をSQLAlchemyの層でブロックすることを確認。
    *   AST解析機構によるスキーマファイルの変更テストにて、セキュリティ要件を満たさない不正なコードや破壊的変更が正しく弾かれることを検証。

*※ 本リポジトリは、これらの堅牢なバックエンド基盤の「核（コア）」となる部分を先行公開するものです。*
