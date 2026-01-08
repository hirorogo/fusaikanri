# fusaikanri - VPSセットアップガイド

このガイドでは、VPS（Virtual Private Server）上でfusaikanri Discord Botをデプロイし、24時間稼働させる方法を説明します。

## 目次

- [前提条件](#前提条件)
- [VPS初期設定](#vps初期設定)
- [Botのデプロイ](#botのデプロイ)
- [systemdサービス化](#systemdサービス化)
- [自動起動設定](#自動起動設定)
- [ログ管理](#ログ管理)
- [バックアップ設定](#バックアップ設定)
- [アップデート方法](#アップデート方法)
- [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

### 必要なもの
- VPS（推奨: Ubuntu 20.04/22.04, Debian 11/12, CentOS 8以上）
- rootまたはsudo権限を持つユーザー
- Discord Botトークン
- SSH接続環境

### 推奨スペック
- **CPU**: 1コア以上
- **メモリ**: 512MB以上（1GB推奨）
- **ストレージ**: 10GB以上
- **OS**: Ubuntu 22.04 LTS（本ガイドではUbuntuを想定）

---

## VPS初期設定

### 1. VPSにSSH接続

```bash
ssh username@your-vps-ip
```

### 2. システムアップデート

```bash
sudo apt update && sudo apt upgrade -y
```

### 3. 必要なパッケージをインストール

```bash
# Python 3.11以上とgitをインストール
sudo apt install -y python3 python3-pip python3-venv git

# 必要に応じてその他のツールもインストール
sudo apt install -y curl wget vim htop
```

### 4. タイムゾーン設定（任意）

```bash
sudo timedatectl set-timezone Asia/Tokyo
```

### 5. ファイアウォール設定（任意だが推奨）

```bash
# UFWをインストール・有効化
sudo apt install -y ufw
sudo ufw allow ssh
sudo ufw enable
```

---

## Botのデプロイ

### 1. 専用ユーザーの作成（推奨）

セキュリティのため、Bot専用のユーザーを作成します。

```bash
# botユーザーを作成
sudo adduser fusaikanri

# sudoグループに追加（必要に応じて）
sudo usermod -aG sudo fusaikanri

# botユーザーに切り替え
su - fusaikanri
```

### 2. リポジトリをクローン

```bash
cd ~
git clone https://github.com/hirorogo/fusaikanri.git
cd fusaikanri
```

### 3. Python仮想環境の作成

```bash
# 仮想環境を作成
python3 -m venv venv

# 仮想環境を有効化
source venv/bin/activate
```

### 4. 依存関係をインストール

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. 環境変数を設定

```bash
# .envファイルを作成
cp .env.example .env

# .envファイルを編集
nano .env
```

以下の内容を設定：

```env
DISCORD_TOKEN=your_discord_bot_token_here
COMMAND_PREFIX=!
LOG_LEVEL=INFO
DATA_DIR=data
```

保存して終了（Ctrl+O → Enter → Ctrl+X）

### 6. 動作確認

```bash
# 仮想環境が有効化されていることを確認
source venv/bin/activate

# Botを起動
python3 bot.py
```

正常に起動したら`Ctrl+C`で停止します。

---

## systemdサービス化

Botを常時稼働させるため、systemdサービスとして登録します。

### 1. サービスファイルを作成

```bash
sudo nano /etc/systemd/system/fusaikanri.service
```

以下の内容を貼り付け：

```ini
[Unit]
Description=fusaikanri Discord Bot
After=network.target

[Service]
Type=simple
User=fusaikanri
WorkingDirectory=/home/fusaikanri/fusaikanri
Environment="PATH=/home/fusaikanri/fusaikanri/venv/bin"
ExecStart=/home/fusaikanri/fusaikanri/venv/bin/python3 /home/fusaikanri/fusaikanri/bot.py
Restart=always
RestartSec=10

# ログ設定
StandardOutput=append:/home/fusaikanri/fusaikanri/logs/bot.log
StandardError=append:/home/fusaikanri/fusaikanri/logs/error.log

[Install]
WantedBy=multi-user.target
```

**注意**: `User`と`WorkingDirectory`は環境に合わせて変更してください。

### 2. ログディレクトリを作成

```bash
mkdir -p ~/fusaikanri/logs
```

### 3. サービスを有効化

```bash
# systemdをリロード
sudo systemctl daemon-reload

# サービスを有効化（自動起動）
sudo systemctl enable fusaikanri

# サービスを起動
sudo systemctl start fusaikanri
```

### 4. サービス状態を確認

```bash
# サービスの状態を確認
sudo systemctl status fusaikanri

# ログをリアルタイムで確認
tail -f ~/fusaikanri/logs/bot.log
```

---

## 自動起動設定

systemdサービスとして登録済みなので、VPS再起動時に自動的にBotが起動します。

### 動作確認

```bash
# VPSを再起動
sudo reboot

# 再接続後、サービスが起動しているか確認
sudo systemctl status fusaikanri
```

---

## ログ管理

### ログの確認

```bash
# 最新のログを表示
tail -n 50 ~/fusaikanri/logs/bot.log

# エラーログを表示
tail -n 50 ~/fusaikanri/logs/error.log

# リアルタイムでログを監視
tail -f ~/fusaikanri/logs/bot.log
```

### ログローテーション設定（推奨）

ログファイルが肥大化するのを防ぐため、logrotateを設定します。

```bash
sudo nano /etc/logrotate.d/fusaikanri
```

以下の内容を貼り付け：

```
/home/fusaikanri/fusaikanri/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 fusaikanri fusaikanri
}
```

---

## バックアップ設定

### 手動バックアップ

```bash
# データファイルをバックアップ
cp ~/fusaikanri/data/debts.json ~/fusaikanri/data/debts_backup_$(date +%Y%m%d).json
```

### 自動バックアップ（cron）

```bash
# cronを編集
crontab -e
```

以下を追加（毎日午前3時にバックアップ）：

```cron
0 3 * * * cp ~/fusaikanri/data/debts.json ~/fusaikanri/data/debts_backup_$(date +\%Y\%m\%d).json
```

### バックアップをローカルにダウンロード

```bash
# ローカルマシンから実行
scp username@your-vps-ip:~/fusaikanri/data/debts.json ~/backup/
```

---

## アップデート方法

### 1. 最新版を取得

```bash
cd ~/fusaikanri

# 変更を一時退避（必要に応じて）
git stash

# 最新版を取得
git pull origin main

# 退避した変更を戻す（必要に応じて）
git stash pop
```

### 2. 依存関係を更新

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### 3. Botを再起動

```bash
sudo systemctl restart fusaikanri

# ログで正常起動を確認
tail -f ~/fusaikanri/logs/bot.log
```

---

## トラブルシューティング

### Botが起動しない

#### 1. サービス状態を確認

```bash
sudo systemctl status fusaikanri
```

#### 2. ログを確認

```bash
tail -n 100 ~/fusaikanri/logs/error.log
```

#### 3. 手動起動してエラーを確認

```bash
cd ~/fusaikanri
source venv/bin/activate
python3 bot.py
```

### よくあるエラー

#### `ModuleNotFoundError: No module named 'discord'`

依存関係が正しくインストールされていません。

```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### `discord.errors.LoginFailure: Improper token has been passed`

Discord Botトークンが間違っています。

```bash
nano .env
# DISCORD_TOKENを正しい値に修正
sudo systemctl restart fusaikanri
```

#### サービスが自動起動しない

```bash
# サービスを有効化
sudo systemctl enable fusaikanri

# 起動
sudo systemctl start fusaikanri
```

### コマンドが同期されない

```bash
# Botを再起動
sudo systemctl restart fusaikanri

# Discord側でコマンドが反映されるまで数分待つ
```

---

## セキュリティのベストプラクティス

### 1. ファイアウォール設定

```bash
# SSH以外は基本的に閉じる
sudo ufw allow ssh
sudo ufw enable
```

### 2. SSH鍵認証の使用

パスワード認証を無効化し、SSH鍵認証を使用することを推奨します。

### 3. 定期的なアップデート

```bash
# 週1回程度実行
sudo apt update && sudo apt upgrade -y
```

### 4. .envファイルの権限設定

```bash
chmod 600 ~/fusaikanri/.env
```

---

## 便利なコマンド集

```bash
# サービスの起動
sudo systemctl start fusaikanri

# サービスの停止
sudo systemctl stop fusaikanri

# サービスの再起動
sudo systemctl restart fusaikanri

# サービスの状態確認
sudo systemctl status fusaikanri

# ログのリアルタイム監視
tail -f ~/fusaikanri/logs/bot.log

# ディスク使用量確認
df -h

# メモリ使用量確認
free -h

# プロセス確認
ps aux | grep python
```

---

## 参考リンク

- [ローカル環境セットアップガイド](./SETUP.md) - ローカルでの開発環境構築方法
- [README.md](./README.md) - プロジェクト概要とコマンド一覧
- [Discord Developer Portal](https://discord.com/developers/applications) - Botトークンの取得
- [systemd Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

## サポート

問題が発生した場合は、GitHubのIssueで報告してください。

- GitHub: https://github.com/hirorogo/fusaikanri
