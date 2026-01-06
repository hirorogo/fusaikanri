"""
fusaikanri - Discord Bot for Managing Debt/Technical Debt

This bot helps manage and track debt items on Discord servers.
"""
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('COMMAND_PREFIX', '!')

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# Create bot instance
bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    """Event handler for when the bot is ready."""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')


@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('コマンドが見つかりません。')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('必要な引数が不足しています。')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('このコマンドを実行する権限がありません。')
    else:
        print(f'Error: {error}')
        await ctx.send('エラーが発生しました。')


@bot.command(name='ping')
async def ping(ctx):
    """Check if the bot is responsive."""
    await ctx.send(f'Pong! レイテンシ: {round(bot.latency * 1000)}ms')


@bot.command(name='hello')
async def hello(ctx):
    """Greet the user."""
    await ctx.send(f'こんにちは、{ctx.author.mention}さん！')


def main():
    """Main function to run the bot."""
    if not TOKEN:
        print('Error: DISCORD_TOKEN not found in environment variables.')
        print('Please create a .env file with your Discord bot token.')
        return
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print('Error: Invalid token. Please check your DISCORD_TOKEN.')
    except Exception as e:
        print(f'Error starting bot: {e}')


if __name__ == '__main__':
    main()
