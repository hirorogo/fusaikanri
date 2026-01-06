# fusaikanri
Discord server上で負債を管理するためのbot

## セットアップ

### 必要要件
- Python 3.8以上
- Discordボットトークン

### インストール手順

1. リポジトリをクローン
```bash
git clone https://github.com/hirorogo/fusaikanri.git
cd fusaikanri
```

2. 依存関係をインストール
```bash
pip install -r requirements.txt
```

3. 環境変数を設定
```bash
cp .env.example .env
# .envファイルを編集してDISCORD_TOKENを設定
```

4. ボットを起動
```bash
python bot.py
```

## 使用方法

基本的なコマンド：
- `!ping` - ボットの応答確認
- `!hello` - 挨拶

## ファイル構成

- `bot.py` - メインのボットファイル
- `requirements.txt` - Python依存関係
- `.env.example` - 環境変数のテンプレート
- `.github/copilot-instructions.md` - GitHub Copilotの指示ファイル
