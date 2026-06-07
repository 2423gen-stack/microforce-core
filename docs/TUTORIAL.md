# Microforce-Coer V3: チュートリアル (Tutorial)

従来のRDBMS（SQLベース）から「Semantic KVS」へのパラダイムシフトを体験するためのチュートリアルです。
「ORMのマッピングをせずに、JSONデータ構造をまるごと保存・取得する」という快感を実際に試してみてください。

## 準備

まずは仮想環境に入り、依存パッケージをインストールします。

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 遊び方 1: ダミーデータの「丸呑み」を体験する

従来のRDBMSなら、`products`, `categories`, `metadata` などのテーブルを作り、外部キーで繋ぐ必要がありました。
しかしSemantic KVSでは、複雑なネストを持ったJSONデータをそのまま「1つのレイヤー」として放り込みます。

`backend/data/dummy_catalog.json` に、ネストされた商品データのサンプルを用意しています。
これをKVSに読み書きしてみましょう。

対話型Python（REPL）を開きます：
```bash
python3
```

以下のコードをコピペして実行してみてください。

```python
import asyncio
import json
from src.database.engine_v3 import init_v3_db
from src.mcp_tools.kvs_tools import write_layer, read_layer

async def play():
    # 1. データベースの初期化
    await init_v3_db()
    
    # 2. ダミーデータ（複雑なJSON）の読み込み
    with open("data/dummy_catalog.json", "r") as f:
        payload = f.read()
    
    # 3. KVSに「丸呑み」させる (INSERT)
    print("Writing payload to KVS...")
    await write_layer(layer_key="catalog:summer_2026", layer_type="product_data", payload_json=payload)
    print("Done! No SQL schema required.")

    # 4. KVSから取り出す (SELECT)
    print("\nRetrieving from KVS...")
    retrieved = await read_layer("catalog:summer_2026")
    
    # 5. 取り出したデータ（文字列）を辞書に戻してアクセス
    data_dict = json.loads(retrieved)
    items = data_dict["payload"]["items"]
    
    print("\n--- 商品一覧 ---")
    for item in items:
        print(f"- {item['name']} (¥{item['price']}) - Stock: {item['stock']}")

# 実行
asyncio.run(play())
```

**結果はどうなりましたか？**
テーブル定義や `CREATE TABLE`、ORMのマッピングクラスを一切書くことなく、ネストされた商品リストを一瞬で保存し、取り出すことができました。
これが「AIネイティブなデータ構造」の力です。

## 遊び方 2: Pandas データフレームの丸呑み

表形式（二次元配列）のデータも同様に保存できます。

```bash
python3 scripts/example_pandas_kvs.py
```
このスクリプトは、Pandas DataFrameをJSONに変換してそのままKVSに保存し、再度KVSから読み出してDataFrameに復元するデモンストレーションを行います。

## 次のステップ
データ構造は自由自在です。`payload` にはどんなJSONでも入ります。
AIエージェント（MCPクライアント）から `write_layer` と `read_layer` ツールを呼び出すことで、AIが自律的にスキーマやデータを構築していく様を観察することができます。
