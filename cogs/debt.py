"""
debt.py - 借金管理コマンドCog

借金の追加、返済、一覧表示、債権譲渡などの機能を提供する
"""
import discord;
from discord import app_commands;
from discord.ext import commands;
from typing import Optional;
import sys;
import os;

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))));

from utils.database import DebtDatabase;

class DebtCog(commands.Cog):
  """
  借金管理Cogクラス
  """
  
  def __init__(self, bot: commands.Bot):
    """
    Cogを初期化する
    
    Args:
      bot: Botインスタンス
    """
    self.bot = bot;
    self.db = DebtDatabase();
  
  debt_group = app_commands.Group(name="debt", description="お金の貸し借りを管理するコマンド");
  
  @debt_group.command(name="borrow", description="相手からお金を借りたことを記録する")
  @app_commands.describe(
    user="お金を貸してくれた人",
    amount="借りた金額",
    description="何のために借りたか（例: ランチ代）"
  )
  async def borrow_money(
    self, 
    interaction: discord.Interaction, 
    user: discord.User, 
    amount: int,
    description: Optional[str] = ""
  ):
    """
    お金を借りたことを記録するコマンド
    
    Args:
      interaction: インタラクション
      user: お金を貸してくれた人
      amount: 借りた金額
      description: 説明
    """
    if amount <= 0:
      await interaction.response.send_message("金額は1円以上を指定してくれ", ephemeral=True);
      return;
    
    if user.id == interaction.user.id:
      await interaction.response.send_message("自分から自分に借りることはできないぞ", ephemeral=True);
      return;
    
    # 借金を追加（userが債権者、interaction.userが債務者）
    success = self.db.add_debt(user.id, interaction.user.id, amount, description);
    
    if success:
      # 現在の総借金額を取得
      total_debt = self.db.get_debt(user.id, interaction.user.id);
      
      # ログチャンネルに送信
      await self._send_log(
        interaction.guild.id,
        f"{interaction.user.mention}は{user.mention}から{amount}円借りた！\n"
        f"累計{total_debt}円！はよ返せよな！"
      );
      
      await interaction.response.send_message(
        f"{user.mention}から{amount}円借りた！\n"
        f"累計: {total_debt}円",
        ephemeral=False
      );
    else:
      await interaction.response.send_message("記録に失敗した", ephemeral=True);
  
  @debt_group.command(name="lend", description="相手に貸したことを記録する")
  @app_commands.describe(
    user="お金を貸した相手",
    amount="貸した金額",
    description="メモ）"
  )
  async def lend_money(
    self, 
    interaction: discord.Interaction, 
    user: discord.User, 
    amount: int,
    description: Optional[str] = ""
  ):
    """
    お金を貸したことを記録するコマンド
    
    Args:
      interaction: インタラクション
      user: お金を貸した相手
      amount: 貸した金額
      description: 説明
    """
    if amount <= 0:
      await interaction.response.send_message("金額は1円以上を指定してくれ", ephemeral=True);
      return;
    
    if user.id == interaction.user.id:
      await interaction.response.send_message("自分に自分で貸すことはできないぞ", ephemeral=True);
      return;
    
    # 借金を追加（interaction.userが債権者、userが債務者）
    success = self.db.add_debt(interaction.user.id, user.id, amount, description);
    
    if success:
      # 現在の総借金額を取得
      total_debt = self.db.get_debt(interaction.user.id, user.id);
      
      # ログチャンネルに送信
      await self._send_log(
        interaction.guild.id,
        f"{interaction.user.mention}は{user.mention}に{amount}円貸した！\n"
        f"累計{total_debt}円！{user.mention}はよ返せよな！"
      );
      
      await interaction.response.send_message(
        f"{user.mention}に{amount}円貸した！\n"
        f"累計: {total_debt}円",
        ephemeral=False
      );
    else:
      await interaction.response.send_message("記録に失敗した", ephemeral=True);
  
  @debt_group.command(name="pay", description="借りたお金を返済する")
  @app_commands.describe(
    user="返済先（お金を貸してくれた人）",
    amount="返済する金額"
  )
  async def pay_debt(
    self,
    interaction: discord.Interaction,
    user: discord.User,
    amount: int
  ):
    """
    借金を返済するコマンド
    
    Args:
      interaction: インタラクション
      user: 返済先
      amount: 返済額
    """
    if amount <= 0:
      await interaction.response.send_message("金額は1円以上を指定してくれ", ephemeral=True);
      return;
    
    # 借金を返済（userが債権者、interaction.userが債務者）
    success, remaining = self.db.pay_debt(user.id, interaction.user.id, amount);
    
    if not success:
      await interaction.response.send_message(
        f"{user.mention}からは借りてないか、金額が多すぎるぞ",
        ephemeral=True
      );
      return;
    
    # ログチャンネルに送信
    if remaining == 0:
      await self._send_log(
        interaction.guild.id,
        f"{interaction.user.mention}は{user.mention}に{amount}円返済した！\n"
        f"完済だ！おつかれ！"
      );
      await interaction.response.send_message(
        f"{user.mention}に{amount:,}円返済した！完済だ！",
        ephemeral=False
      );
    else:
      await self._send_log(
        interaction.guild.id,
        f"{interaction.user.mention}は{user.mention}に{amount}円返済した！\n"
        f"残りの借金は{remaining}円だぞ！"
      );
      await interaction.response.send_message(
        f"{user.mention}に{amount:,}円返済した！\n残り: {remaining:,}円",
        ephemeral=False
      );
  
  @debt_group.command(name="pay_on_behalf", description="他の人の借金を代わりに返済する")
  @app_commands.describe(
    debtor="債務者（借りている人）",
    creditor="債権者（貸している人）",
    amount="返済額"
  )
  async def pay_on_behalf(
    self,
    interaction: discord.Interaction,
    debtor: discord.User,
    creditor: discord.User,
    amount: int
  ):
    """
    他の人の借金を代わりに返済するコマンド
    
    Args:
      interaction: インタラクション
      debtor: 債務者
      creditor: 債権者
      amount: 返済額
    """
    if amount <= 0:
      await interaction.response.send_message("金額は1円以上を指定してくれ", ephemeral=True);
      return;
    
    if debtor.id == interaction.user.id:
      await interaction.response.send_message(
        "自分の借金は /debt pay を使ってくれ",
        ephemeral=True
      );
      return;
    
    if creditor.id == debtor.id:
      await interaction.response.send_message(
        "債権者と債務者が同じ人だぞ！正しい相手を指定してくれ",
        ephemeral=True
      );
      return;
    
    # 借金を返済（creditorが債権者、debtorが債務者、interaction.userが代理で返済）
    # NOTE: 権限チェックなし - 身内で使うため誰でも代理返済可能
    success, remaining = self.db.pay_debt(creditor.id, debtor.id, amount, interaction.user.id);
    
    if not success:
      await interaction.response.send_message(
        f"{debtor.mention}の{creditor.mention}への借金がないか、金額が多すぎるぞ",
        ephemeral=True
      );
      return;
    
    # ログチャンネルに送信
    if remaining == 0:
      await self._send_log(
        interaction.guild.id,
        f"{interaction.user.mention}が{debtor.mention}の代わりに{creditor.mention}へ{amount}円返済した！\n"
        f"完済だ！おつかれ！"
      );
      await interaction.response.send_message(
        f"{debtor.mention}の代わりに{creditor.mention}へ{amount}円返済した！完済だ！",
        ephemeral=False
      );
    else:
      await self._send_log(
        interaction.guild.id,
        f"{interaction.user.mention}が{debtor.mention}の代わりに{creditor.mention}へ{amount}円返済した！\n"
        f"残りの借金は{remaining}円だぞ！"
      );
      await interaction.response.send_message(
        f"{debtor.mention}の代わりに{creditor.mention}へ{amount}円返済した！\n残り: {remaining}円",
        ephemeral=False
      );
  
  @debt_group.command(name="list", description="自分の貸し借り一覧を表示する")
  async def list_debts(self, interaction: discord.Interaction):
    """
    貸し借り一覧を表示するコマンド
    
    Args:
      interaction: インタラクション
    """
    debts = self.db.get_user_debts(interaction.user.id);
    
    embed = discord.Embed(
      title=f"{interaction.user.display_name}の貸し借り一覧",
      color=discord.Color.blue()
    );
    
    # 貸している分
    if debts["creditor"]:
      creditor_list = [];
      total_lent = 0;
      for debtor_id, amount in debts["creditor"]:
        user = await self.bot.fetch_user(debtor_id);
        creditor_list.append(f"- {user.mention}に: {amount:,}円");
        total_lent += amount;
      embed.add_field(
        name=f"貸している（合計: {total_lent:,}円）",
        value="\n".join(creditor_list),
        inline=False
      );
    else:
      embed.add_field(name="貸している", value="なし", inline=False);
    
    # 借りている分
    if debts["debtor"]:
      debtor_list = [];
      total_borrowed = 0;
      for creditor_id, amount in debts["debtor"]:
        user = await self.bot.fetch_user(creditor_id);
        debtor_list.append(f"- {user.mention}から: {amount:,}円");
        total_borrowed += amount;
      embed.add_field(
        name=f"借りている（合計: {total_borrowed:,}円）",
        value="\n".join(debtor_list),
        inline=False
      );
    else:
      embed.add_field(name="借りている", value="なし", inline=False);
    
    await interaction.response.send_message(embed=embed, ephemeral=True);
  
  @debt_group.command(name="status", description="特定のユーザーとの収支を確認する")
  @app_commands.describe(user="確認相手")
  async def status(self, interaction: discord.Interaction, user: discord.User):
    """
    特定のユーザーとの収支を確認するコマンド
    
    Args:
      interaction: インタラクション
      user: 確認相手
    """
    # 自分が貸している分
    lending = self.db.get_debt(interaction.user.id, user.id);
    # 自分が借りている分
    borrowing = self.db.get_debt(user.id, interaction.user.id);
    
    embed = discord.Embed(
      title=f"{interaction.user.display_name} ⇔ {user.display_name}",
      color=discord.Color.green()
    );
    
    embed.add_field(name="貸している", value=f"{lending}円", inline=True);
    embed.add_field(name="借りている", value=f"{borrowing}円", inline=True);
    
    balance = lending - borrowing;
    if balance > 0:
      embed.add_field(name="収支", value=f"+{balance}円（プラス）", inline=False);
    elif balance < 0:
      embed.add_field(name="収支", value=f"{balance}円（マイナス）", inline=False);
    else:
      embed.add_field(name="収支", value="±0円（イーブン）", inline=False);
    
    await interaction.response.send_message(embed=embed, ephemeral=True);
  
  @debt_group.command(name="history", description="取引履歴を表示する")
  async def history(self, interaction: discord.Interaction):
    """
    取引履歴を表示するコマンド
    
    Args:
      interaction: インタラクション
    """
    history = self.db.get_history(interaction.user.id, limit=10);
    
    if not history:
      await interaction.response.send_message("履歴がないぞ", ephemeral=True);
      return;
    
    embed = discord.Embed(
      title=f"{interaction.user.display_name}の取引履歴",
      color=discord.Color.gold()
    );
    
    for h in reversed(history):
      action_text = {
        "add": "借金追加",
        "pay": "返済",
        "transfer": "債権譲渡"
      }.get(h["action"], h["action"]);
      
      creditor = await self.bot.fetch_user(int(h["creditor"]));
      debtor = await self.bot.fetch_user(int(h["debtor"]));
      
      embed.add_field(
        name=f"{action_text} - {h['timestamp'][:10]}",
        value=f"{creditor.display_name} → {debtor.display_name}: {h['amount']}円",
        inline=False
      );
    
    await interaction.response.send_message(embed=embed, ephemeral=True);
  
  @debt_group.command(name="summary", description="全体の借金サマリーを表示する")
  async def summary(self, interaction: discord.Interaction):
    """
    全体の借金サマリーを表示するコマンド
    
    Args:
      interaction: インタラクション
    """
    summary = self.db.get_summary();
    
    embed = discord.Embed(
      title="借金サマリー",
      description="サーバー全体の借金状況だぞ",
      color=discord.Color.purple()
    );
    
    # 基本統計
    embed.add_field(
      name="総借金額",
      value=f"{summary['total_debts']:,}円",
      inline=True
    );
    embed.add_field(
      name="関係者数",
      value=f"{summary['total_users']}人",
      inline=True
    );
    
    # トップ債権者（貸している人）
    if summary["top_creditors"]:
      creditor_list = [];
      for i, (user_id, amount) in enumerate(summary["top_creditors"], 1):
        try:
          user = await self.bot.fetch_user(user_id);
          creditor_list.append(f"{i}. {user.display_name}: {amount:,}円");
        except (discord.NotFound, discord.HTTPException):
          creditor_list.append(f"{i}. ユーザー#{user_id}: {amount:,}円");
      
      embed.add_field(
        name="トップ債権者（貸してる）",
        value="\n".join(creditor_list) if creditor_list else "なし",
        inline=False
      );
    
    # トップ債務者（借りている人）
    if summary["top_debtors"]:
      debtor_list = [];
      for i, (user_id, amount) in enumerate(summary["top_debtors"], 1):
        try:
          user = await self.bot.fetch_user(user_id);
          debtor_list.append(f"{i}. {user.display_name}: {amount:,}円");
        except (discord.NotFound, discord.HTTPException):
          debtor_list.append(f"{i}. ユーザー#{user_id}: {amount:,}円");
      
      embed.add_field(
        name="トップ債務者（借りてる）",
        value="\n".join(debtor_list) if debtor_list else "なし",
        inline=False
      );
    
    await interaction.response.send_message(embed=embed, ephemeral=False);
  
  @debt_group.command(name="transfer", description="債権を譲渡する")
  @app_commands.describe(
    debtor="債務者（借りている人）",
    new_creditor="譲渡先（新しい債権者）",
    amount="譲渡額"
  )
  async def transfer_debt(
    self,
    interaction: discord.Interaction,
    debtor: discord.User,
    new_creditor: discord.User,
    amount: int
  ):
    """
    債権を譲渡するコマンド
    
    Args:
      interaction: インタラクション
      debtor: 債務者
      new_creditor: 新しい債権者
      amount: 譲渡額
    """
    if amount <= 0:
      await interaction.response.send_message("金額は1円以上を指定してくれ", ephemeral=True);
      return;
    
    if debtor.id == interaction.user.id or new_creditor.id == interaction.user.id:
      await interaction.response.send_message("不正な譲渡だぞ", ephemeral=True);
      return;
    
    # 債権を譲渡
    success, error_msg, remaining = self.db.transfer_debt(
      interaction.user.id,
      debtor.id,
      new_creditor.id,
      amount
    );
    
    if not success:
      await interaction.response.send_message(f"エラー: {error_msg}", ephemeral=True);
      return;
    
    # ログチャンネルに送信
    await self._send_log(
      interaction.guild.id,
      f"{interaction.user.mention}は{new_creditor.mention}に債権{amount}円を譲渡した！\n"
      f"{debtor.mention}は{new_creditor.mention}に{amount}円返せよな！\n"
      f"（{interaction.user.mention}の残債権: {remaining}円）"
    );
    
    await interaction.response.send_message(
      f"{new_creditor.mention}に{debtor.mention}への債権{amount}円を譲渡した！\n"
      f"残りの債権: {remaining}円",
      ephemeral=False
    );
  
  config_group = app_commands.Group(name="config", description="設定コマンド", parent=debt_group);
  
  @config_group.command(name="transfer", description="債権譲渡機能の有効/無効を設定する")
  @app_commands.describe(mode="enable: 有効化, disable: 無効化")
  @app_commands.choices(mode=[
    app_commands.Choice(name="enable", value="enable"),
    app_commands.Choice(name="disable", value="disable")
  ])
  async def config_transfer(self, interaction: discord.Interaction, mode: str):
    """
    債権譲渡機能の有効/無効を設定するコマンド
    
    Args:
      interaction: インタラクション
      mode: enable/disable
    """
    enabled = (mode == "enable");
    success = self.db.set_transfer_enabled(interaction.user.id, enabled);
    
    if success:
      status_text = "有効" if enabled else "無効";
      await interaction.response.send_message(
        f"債権譲渡機能を{status_text}にした！",
        ephemeral=True
      );
    else:
      await interaction.response.send_message("設定の保存に失敗した", ephemeral=True);
  
  @app_commands.command(name="set", description="ログチャンネルを設定する")
  @app_commands.describe(channel="ログを流すチャンネル")
  @app_commands.default_permissions(administrator=True)
  async def set_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
    """
    ログチャンネルを設定するコマンド
    
    Args:
      interaction: インタラクション
      channel: チャンネル
    """
    success = self.db.set_log_channel(interaction.guild.id, channel.id);
    
    if success:
      await interaction.response.send_message(
        f"ログチャンネルを{channel.mention}に設定した！",
        ephemeral=True
      );
    else:
      await interaction.response.send_message("設定の保存に失敗した", ephemeral=True);
  
  async def _send_log(self, guild_id: int, message: str):
    """
    ログチャンネルにメッセージを送信する
    
    Args:
      guild_id: サーバーID
      message: メッセージ
    """
    channel_id = self.db.get_log_channel(guild_id);
    if channel_id:
      channel = self.bot.get_channel(channel_id);
      if channel:
        await channel.send(message);

async def setup(bot: commands.Bot):
  """
  Cogをセットアップする
  
  Args:
    bot: Botインスタンス
  """
  await bot.add_cog(DebtCog(bot));
