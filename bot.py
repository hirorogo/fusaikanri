"""
fusaikanri - Discord Bot for Managing Debt/Technical Debt

借金管理を行うDiscord Bot
"""
import os;
import logging;
import discord;
from discord.ext import commands;
from config import Config;

# 設定の検証
if not Config.validate():
  print("エラー: DISCORD_TOKENが設定されていない");
  print(".envファイルにDISCORD_TOKENを設定してください");
  exit(1);

# ログ設定
logging.basicConfig(
  level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
);
logger = logging.getLogger('fusaikanri');

# インテント設定
intents = discord.Intents.default();
intents.message_content = True;
intents.guilds = True;
intents.members = True;

# Botインスタンス作成
bot = commands.Bot(command_prefix=Config.COMMAND_PREFIX, intents=intents);


@bot.event
async def on_ready():
  """Botが起動したときのイベントハンドラ"""
  logger.info(f'{bot.user} が Discord に接続した！');
  logger.info(f'Bot は {len(bot.guilds)} サーバーに参加している');
  
  # Cogを読み込む
  try:
    await bot.load_extension('cogs.debt');
    logger.info('debt Cogを読み込んだ');
  except Exception as e:
    logger.error(f'Cog読み込みエラー: {e}', exc_info=True);
  
  # スラッシュコマンドを同期
  try:
    synced = await bot.tree.sync();
    logger.info(f'{len(synced)} 個のスラッシュコマンドを同期');
  except Exception as e:
    logger.error(f'コマンド同期エラー: {e}', exc_info=True);


@bot.event
async def on_command_error(ctx, error):
  """コマンドエラーのグローバルハンドラ"""
  if isinstance(error, commands.CommandNotFound):
    await ctx.send('コマンドが見つからないぞ');
  elif isinstance(error, commands.MissingRequiredArgument):
    await ctx.send('必要な引数が不足してるぞ');
  elif isinstance(error, commands.MissingPermissions):
    await ctx.send('このコマンドを実行する権限がないぞ');
  else:
    logger.error(f'未処理のコマンドエラー: {error}', exc_info=True);
    await ctx.send('エラーが発生した');


@bot.command(name='ping')
async def ping(ctx):
  """Botの応答確認コマンド"""
  await ctx.send(f'Pong! レイテンシ: {round(bot.latency * 1000)}ms');


@bot.command(name='hello')
async def hello(ctx):
  """挨拶コマンド"""
  await ctx.send(f'よう、{ctx.author.mention}！');


def main():
  """メイン関数 - Botを起動する"""
  try:
    bot.run(Config.DISCORD_TOKEN);
  except discord.LoginFailure:
    logger.error('トークンが無効。DISCORD_TOKENを確認してくれ');
  except Exception as e:
    logger.error(f'Bot起動エラー: {e}', exc_info=True);


if __name__ == '__main__':
  main();
