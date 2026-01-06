"""
config.py - 設定管理モジュール

Botの設定を管理する
"""
import os;
from dotenv import load_dotenv;

# 環境変数を読み込む
load_dotenv();

class Config:
  """
  設定クラス
  環境変数から設定を読み込む
  """
  
  # Discordトークン
  DISCORD_TOKEN = os.getenv('DISCORD_TOKEN');
  
  # コマンドプレフィックス
  COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!');
  
  # ログレベル
  LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO');
  
  # データベースパス
  DATA_DIR = os.getenv('DATA_DIR', 'data');
  DB_PATH = os.path.join(DATA_DIR, 'debts.json');
  
  @classmethod
  def validate(cls) -> bool:
    """
    設定が有効かどうかを検証する
    
    Returns:
      bool: 設定が有効な場合True
    """
    if not cls.DISCORD_TOKEN:
      return False;
    return True;
