import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
from flask import Flask
import threading

# Carica le variabili d'ambiente
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Web server per keep-alive
app = Flask('')

@app.route('/')
def home():
    return "Bot attivo!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

@bot.event
async def on_ready():
    print(f"✅ Bot connesso come {bot.user}")
    weekly_poll.start()
    monthly_poll.start()

@bot.command(name="testsondaggi")
async def test_sondaggi(ctx):
    if ctx.channel.id != CHANNEL_ID:
        await ctx.send("Usa questo comando solo nel canale corretto.")
        return
    await invia_sondaggi(ctx.channel)

async def invia_sondaggi(channel):
    # Domanda 1
    await channel.send("📊 **Com'è andata la settimana?**\n\n"
                       "👍 Positiva\n\n"
                       "👎 Negativa\n\n"
                       "🤷 Ho chiuso la settimana in pari\n\n"
                       "\n⬇️ Vota con una reazione qui sotto:")

    msg1 = await channel.history(limit=1).flatten()
    msg1 = msg1[0]
    await msg1.add_reaction("👍")
    await msg1.add_reaction("👎")
    await msg1.add_reaction("🤷")

    # Domanda 2
    await channel.send("\n📈 **Quanto capitali gestisci attualmente?**\n\n"
                       "💼 Meno di 100k\n\n"
                       "💰 Tra 100k e 500k\n\n"
                       "🏦 Tra 500k e 1 milione\n\n"
                       "🦈 Oltre 1 milione\n\n"
                       "\n⬇️ Vota con una reazione qui sotto:")

    msg2 = await channel.history(limit=1).flatten()
    msg2 = msg2[0]
    await msg2.add_reaction("💼")
    await msg2.add_reaction("💰")
    await msg2.add_reaction("🏦")
    await msg2.add_reaction("🦈")

# Invio automatico settimanale (ogni venerdì alle 20:00)
@tasks.loop(minutes=1)
async def weekly_poll():
    tz = pytz.timezone("Europe/Rome")
    now = datetime.now(tz)
    if now.weekday() == 4 and now.hour == 20 and now.minute == 0:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await invia_sondaggi(channel)

# Invio automatico mensile (ultimo giorno del mese alle 20:00)
@tasks.loop(minutes=1)
async def monthly_poll():
    tz = pytz.timezone("Europe/Rome")
    now = datetime.now(tz)
    tomorrow = now.replace(day=now.day + 1) if now.day < 28 else now
    try:
        tomorrow = now.replace(day=now.day + 1)
    except:
        tomorrow = None
    if tomorrow is None and now.hour == 20 and now.minute == 0:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await invia_sondaggi(channel)

keep_alive()
bot.run(DISCORD_TOKEN)
