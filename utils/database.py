"""
database.py - データベース操作モジュール

借金データの永続化と操作を行う
"""
import json;
import os;
from typing import Dict, List, Optional, Tuple;
from datetime import datetime;
from config import Config;

class DebtDatabase:
  """
  借金データベースクラス
  JSONファイルでデータを管理する
  """
  
  def __init__(self):
    """
    データベースを初期化する
    """
    self.db_path = Config.DB_PATH;
    self.data = self._load_data();
  
  def _load_data(self) -> Dict:
    """
    データをファイルから読み込む
    
    Returns:
      Dict: 読み込んだデータ
    """
    if os.path.exists(self.db_path):
      try:
        with open(self.db_path, 'r', encoding='utf-8') as f:
          return json.load(f);
      except Exception as e:
        print(f"データ読み込みエラー: {e}");
        return self._create_empty_data();
    return self._create_empty_data();
  
  def _create_empty_data(self) -> Dict:
    """
    空のデータ構造を作成する
    
    Returns:
      Dict: 空のデータ構造
    """
    return {
      "debts": {},  # {creditor_id: {debtor_id: amount}}
      "history": [],  # 履歴
      "user_settings": {},  # {user_id: {transfer_enabled: bool}}
      "log_channels": {}  # {guild_id: channel_id}
    };
  
  def _save_data(self) -> bool:
    """
    データをファイルに保存する
    
    Returns:
      bool: 保存成功時True
    """
    try:
      os.makedirs(os.path.dirname(self.db_path), exist_ok=True);
      with open(self.db_path, 'w', encoding='utf-8') as f:
        json.dump(self.data, f, ensure_ascii=False, indent=2);
      return True;
    except Exception as e:
      print(f"データ保存エラー: {e}");
      return False;
  
  def add_debt(self, creditor_id: int, debtor_id: int, amount: int, description: str = "") -> bool:
    """
    借金を追加する
    
    Args:
      creditor_id: 債権者のID（お金を貸す人）
      debtor_id: 債務者のID（お金を借りる人）
      amount: 金額
      description: 説明
    
    Returns:
      bool: 追加成功時True
    """
    creditor_str = str(creditor_id);
    debtor_str = str(debtor_id);
    
    if creditor_str not in self.data["debts"]:
      self.data["debts"][creditor_str] = {};
    
    current_amount = self.data["debts"][creditor_str].get(debtor_str, 0);
    self.data["debts"][creditor_str][debtor_str] = current_amount + amount;
    
    # 履歴を追加
    self._add_history("add", creditor_id, debtor_id, amount, description);
    
    return self._save_data();
  
  def pay_debt(self, creditor_id: int, debtor_id: int, amount: int) -> Tuple[bool, int]:
    """
    借金を返済する
    
    Args:
      creditor_id: 債権者のID
      debtor_id: 債務者のID
      amount: 返済額
    
    Returns:
      Tuple[bool, int]: (成功フラグ, 残りの借金額)
    """
    creditor_str = str(creditor_id);
    debtor_str = str(debtor_id);
    
    if creditor_str not in self.data["debts"]:
      return False, 0;
    
    if debtor_str not in self.data["debts"][creditor_str]:
      return False, 0;
    
    current_amount = self.data["debts"][creditor_str][debtor_str];
    
    if amount > current_amount:
      return False, current_amount;
    
    new_amount = current_amount - amount;
    
    if new_amount == 0:
      del self.data["debts"][creditor_str][debtor_str];
      if not self.data["debts"][creditor_str]:
        del self.data["debts"][creditor_str];
    else:
      self.data["debts"][creditor_str][debtor_str] = new_amount;
    
    # 履歴を追加
    self._add_history("pay", creditor_id, debtor_id, amount, "");
    
    self._save_data();
    return True, new_amount;
  
  def pay_on_behalf(self, payer_id: int, creditor_id: int, debtor_id: int, amount: int) -> Tuple[bool, int]:
    """
    他の人の借金を代わりに返済する
    
    Args:
      payer_id: 返済者のID（代わりに払う人）
      creditor_id: 債権者のID（お金を受け取る人）
      debtor_id: 債務者のID（借金している人）
      amount: 返済額
    
    Returns:
      Tuple[bool, int]: (成功フラグ, 残りの借金額)
    """
    creditor_str = str(creditor_id);
    debtor_str = str(debtor_id);
    
    if creditor_str not in self.data["debts"]:
      return False, 0;
    
    if debtor_str not in self.data["debts"][creditor_str]:
      return False, 0;
    
    current_amount = self.data["debts"][creditor_str][debtor_str];
    
    if amount > current_amount:
      return False, current_amount;
    
    new_amount = current_amount - amount;
    
    if new_amount == 0:
      del self.data["debts"][creditor_str][debtor_str];
      if not self.data["debts"][creditor_str]:
        del self.data["debts"][creditor_str];
    else:
      self.data["debts"][creditor_str][debtor_str] = new_amount;
    
    # 履歴を追加（代理返済であることを記録）
    self._add_history("pay_on_behalf", creditor_id, debtor_id, amount, f"payer:{payer_id}");
    
    self._save_data();
    return True, new_amount;
  
  def get_debt(self, creditor_id: int, debtor_id: int) -> int:
    """
    特定の債権額を取得する
    
    Args:
      creditor_id: 債権者のID
      debtor_id: 債務者のID
    
    Returns:
      int: 債権額
    """
    creditor_str = str(creditor_id);
    debtor_str = str(debtor_id);
    
    if creditor_str in self.data["debts"]:
      return self.data["debts"][creditor_str].get(debtor_str, 0);
    return 0;
  
  def get_user_debts(self, user_id: int) -> Dict[str, List[Tuple[int, int]]]:
    """
    ユーザーの借金一覧を取得する
    
    Args:
      user_id: ユーザーID
    
    Returns:
      Dict: {"creditor": [(debtor_id, amount)], "debtor": [(creditor_id, amount)]}
    """
    user_str = str(user_id);
    result = {"creditor": [], "debtor": []};
    
    # 自分が貸している分
    if user_str in self.data["debts"]:
      for debtor_id, amount in self.data["debts"][user_str].items():
        result["creditor"].append((int(debtor_id), amount));
    
    # 自分が借りている分
    for creditor_id, debtors in self.data["debts"].items():
      if user_str in debtors:
        result["debtor"].append((int(creditor_id), debtors[user_str]));
    
    return result;
  
  def transfer_debt(self, creditor_id: int, debtor_id: int, new_creditor_id: int, amount: int) -> Tuple[bool, str, int]:
    """
    債権を譲渡する
    
    Args:
      creditor_id: 元の債権者ID
      debtor_id: 債務者ID
      new_creditor_id: 新しい債権者ID
      amount: 譲渡額
    
    Returns:
      Tuple[bool, str, int]: (成功フラグ, エラーメッセージ, 残りの債権額)
    """
    # 債権譲渡機能が有効かチェック
    if not self.is_transfer_enabled(creditor_id):
      return False, "債権譲渡機能が無効だぞ！\n/debt config transfer enable で有効化してくれ", 0;
    
    # 債権の存在チェック
    current_debt = self.get_debt(creditor_id, debtor_id);
    if current_debt == 0:
      return False, f"債権がないぞ！", 0;
    
    # 譲渡額のチェック
    if amount > current_debt:
      return False, f"債権は{current_debt}円しかないぞ！", current_debt;
    
    if amount <= 0:
      return False, "金額は1円以上を指定してくれ", current_debt;
    
    # 元の債権者から債権を減らす
    creditor_str = str(creditor_id);
    debtor_str = str(debtor_id);
    new_creditor_str = str(new_creditor_id);
    
    self.data["debts"][creditor_str][debtor_str] -= amount;
    remaining = self.data["debts"][creditor_str][debtor_str];
    
    if self.data["debts"][creditor_str][debtor_str] == 0:
      del self.data["debts"][creditor_str][debtor_str];
      if not self.data["debts"][creditor_str]:
        del self.data["debts"][creditor_str];
    
    # 新しい債権者に債権を追加
    if new_creditor_str not in self.data["debts"]:
      self.data["debts"][new_creditor_str] = {};
    
    current_new_debt = self.data["debts"][new_creditor_str].get(debtor_str, 0);
    self.data["debts"][new_creditor_str][debtor_str] = current_new_debt + amount;
    
    # 履歴を追加
    self._add_history("transfer", creditor_id, debtor_id, amount, f"to:{new_creditor_id}");
    
    self._save_data();
    return True, "", remaining;
  
  def get_history(self, user_id: Optional[int] = None, limit: int = 10) -> List[Dict]:
    """
    履歴を取得する
    
    Args:
      user_id: ユーザーID（指定時はそのユーザーの履歴のみ）
      limit: 取得件数
    
    Returns:
      List[Dict]: 履歴のリスト
    """
    history = self.data["history"];
    
    if user_id:
      user_str = str(user_id);
      history = [h for h in history if h["creditor"] == user_str or h["debtor"] == user_str];
    
    return history[-limit:];
  
  def _add_history(self, action: str, creditor_id: int, debtor_id: int, amount: int, description: str):
    """
    履歴を追加する
    
    Args:
      action: アクション種別（add, pay, pay_on_behalf, transfer）
      creditor_id: 債権者ID
      debtor_id: 債務者ID
      amount: 金額
      description: 説明
    """
    self.data["history"].append({
      "action": action,
      "creditor": str(creditor_id),
      "debtor": str(debtor_id),
      "amount": amount,
      "description": description,
      "timestamp": datetime.now().isoformat()
    });
  
  def set_transfer_enabled(self, user_id: int, enabled: bool) -> bool:
    """
    債権譲渡機能の有効/無効を設定する
    
    Args:
      user_id: ユーザーID
      enabled: 有効フラグ
    
    Returns:
      bool: 設定成功時True
    """
    user_str = str(user_id);
    
    if user_str not in self.data["user_settings"]:
      self.data["user_settings"][user_str] = {};
    
    self.data["user_settings"][user_str]["transfer_enabled"] = enabled;
    return self._save_data();
  
  def is_transfer_enabled(self, user_id: int) -> bool:
    """
    債権譲渡機能が有効かチェックする
    
    Args:
      user_id: ユーザーID
    
    Returns:
      bool: 有効な場合True
    """
    user_str = str(user_id);
    
    if user_str in self.data["user_settings"]:
      return self.data["user_settings"][user_str].get("transfer_enabled", Config.TRANSFER_ENABLED_DEFAULT);
    
    return Config.TRANSFER_ENABLED_DEFAULT;
  
  def set_log_channel(self, guild_id: int, channel_id: int) -> bool:
    """
    ログチャンネルを設定する
    
    Args:
      guild_id: サーバーID
      channel_id: チャンネルID
    
    Returns:
      bool: 設定成功時True
    """
    self.data["log_channels"][str(guild_id)] = channel_id;
    return self._save_data();
  
  def get_log_channel(self, guild_id: int) -> Optional[int]:
    """
    ログチャンネルを取得する
    
    Args:
      guild_id: サーバーID
    
    Returns:
      Optional[int]: チャンネルID
    """
    return self.data["log_channels"].get(str(guild_id));
