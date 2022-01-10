import discord, requests, json
from discord.ext import commands
from fake_useragent import UserAgent


bot = commands.Bot(
    command_prefix="-",
    help_command=None,
    case_insensitive=True,
    intents=discord.Intents.all(),
)
TOKEN = ""


@bot.event
async def on_ready():
    print("Bot is ready")
    await bot.change_presence(
        activity=discord.Game(name=f"Cleaning up grammar in {len(bot.guilds)} servers")
    )


@bot.event
async def on_guild_join(guild):
    with open("settings.json", "r") as f:
        settings = json.load(f)
    settings[str(guild.id)] = True
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)
    await bot.change_presence(
        activity=discord.Game(name=f"Cleaning up grammar in {len(bot.guilds)} servers")
    )


@bot.event
async def on_guild_join(guild):
    with open("settings.json", "r") as f:
        settings = json.load(f)
    del settings[str(guild.id)]
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)
    await bot.change_presence(
        activity=discord.Game(name=f"Cleaning up grammar in {len(bot.guilds)} servers")
    )


@bot.event
async def on_message(message):
    with open("settings.json", "r") as f:
        settings = json.load(f)

    if not message.author.bot and settings[str(message.guild.id)]:

        ua = UserAgent()
        r = requests.post(
            "https://orthographe.reverso.net/api/v1/Spelling",
            headers={"user-agent": ua.random},
            json={
                "language": "eng",
                "text": message.content,
                "autoReplace": True,
                "interfaceLanguage": "en",
                "locale": "Indifferent",
                "origin": "interactive",
                "generateSynonyms": False,
                "generateRecommendations": False,
                "getCorrectionDetails": True,
            },
        )

        if r.json()["text"] != message.content:

            corrected = (
                r.json()["text"]
                if r.json()["text"] != message.content
                else message.content
            )
            url = await message.channel.create_webhook(name="GrammerBot")

            await url.send(
                corrected,
                username=message.author.name,
                avatar_url=message.author.avatar_url,
            )

            await url.delete()
            await message.delete()

    await bot.process_commands(message)


@bot.command()
async def check(ctx):
    with open("settings.json", "r") as f:
        settings = json.load(f)
    try:
        if settings[str(ctx.guild.id)] == True:
            settings[str(ctx.guild.id)] = False
        elif settings[str(ctx.guild.id)] == False:
            settings[str(ctx.guild.id)] = True
    except Exception:
        settings[str(ctx.guild.id)] = True
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)
    await ctx.send(
        f'GrammerBot will now {"check" if settings[str(ctx.guild.id)] else "not check"} for grammatical errors in this server.'
    )


bot.run(TOKEN)
