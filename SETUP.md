# fusaikanri - セットアップガイド

## クイックスタート

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
cp .env.example .env
```

`.env`ファイルを編集して、Discord Botトークンを設定してください：

```
DISCORD_TOKEN=あなたのボットトークン
```

### 3. Discord Developer Portalでの設定

1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセス
2. 新しいアプリケーションを作成
3. Botセクションでトークンを取得
4. OAuth2 > URL Generatorで以下を選択：
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Read Messages/View Channels`, `Use Slash Commands`
5. 生成されたURLでBotをサーバーに招待

### 4. Botの起動

```bash
python bot.py
```

## 初回設定

### ログチャンネルの設定

サーバー管理者権限で以下のコマンドを実行：

```
/set channel:#ログチャンネル名
```

### 債権譲渡機能の有効化（任意）

債権譲渡機能を使いたい場合：

```
/debt config transfer enable
```

## コマンド一覧

### 基本コマンド
- `!ping` - Botの応答確認
- `!hello` - 挨拶

### 借金管理コマンド（スラッシュコマンド）
- `/debt add` - 借金を追加
- `/debt pay` - 借金を返済
- `/debt list` - 自分の借金一覧を表示
- `/debt status` - 特定ユーザーとの収支を確認
- `/debt history` - 取引履歴を表示
- `/debt summary` - サーバー全体の借金サマリーを表示
- `/debt transfer` - 債権を譲渡（要設定）
- `/debt config transfer` - 債権譲渡機能の有効化/無効化

### 管理コマンド
- `/set` - ログチャンネルを設定（管理者のみ）

## トラブルシューティング

### Botが起動しない
- `.env`ファイルが正しく設定されているか確認
- `DISCORD_TOKEN`が正しいか確認

### スラッシュコマンドが表示されない
- Botの権限が正しく設定されているか確認
- Bot招待時に`applications.commands`スコープを含めたか確認
- Botを再起動してみる

### データが保存されない
- `data/`ディレクトリが自動作成されます
- ディスクの書き込み権限を確認

## データのバックアップ

定期的に`data/debts.json`をバックアップすることを推奨します：

```bash
cp data/debts.json data/debts_backup_$(date +%Y%m%d).json
```

## 開発

### Cogの追加

新しい機能を追加する場合は`cogs/`ディレクトリに新しいファイルを作成し、
`bot.py`の`on_ready`関数で`bot.load_extension()`を呼び出してください。

### データベース構造

データは`data/debts.json`に以下の形式で保存されます：

```json
{
  "debts": {
    "債権者ID": {
      "債務者ID": 金額
    }
  },
  "history": [
    {
      "action": "add",
      "creditor": "債権者ID",
      "debtor": "債務者ID",
      "amount": 金額,
      "description": "説明",
      "timestamp": "タイムスタンプ"
    }
  ],
  "user_settings": {
    "ユーザーID": {
      "transfer_enabled": true/false
    }
  },
  "log_channels": {
    "サーバーID": チャンネルID
  }
}
```
