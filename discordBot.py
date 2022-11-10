import discord
from discord.ext import commands
import os
from googletrans import Translator, constants
import dotenv
import speech_recognition
from gtts import gTTS
import asyncio

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
translator = Translator()

global blacklist
global botVoiceChannel
global operator
botVoiceChannel = 0
blacklist = os.environ.get("BLACKLIST").split(",")
operator = os.environ.get("OP")


@bot.command()
async def textTranslate(ctx, *args):
    global blacklist
    auth = ctx.author
    if auth.name in blacklist:
        print("=================================================")
        print("Blacklisted user: ", auth.name)
        print("=================================================")
        return
    args = list(args)
    if len(args) == 1:
        args.append("en")
    if len(args) == 2:
        args.append("pl")
    await ctx.send(doTranslation(input=args[0], fromLang=args[1], toLang=args[2]).text)


@bot.command()
async def voiceTranslate(ctx, *args):
    global blacklist
    global botVoiceChannel
    vc = botVoiceChannel
    auth = ctx.author

    try:
        voiceChannel = auth.voice.channel
    except:
        return

    print(auth.name)
    print(args)

    if auth.name in blacklist:
        print("=================================================")
        print("Blacklisted user: ", auth.name)
        print("=================================================")
        return 0

    if vc != 0:
        args = list(args)
        if len(args) == 1:
            args.append("en")
        if len(args) == 2:
            args.append("pl")

        trans = doTranslation(input=args[0], fromLang=args[1], toLang=args[2])

        # vc = await voiceChannel.connect()
        filename = "tempTranslation.mp3"
        saveTranslationAudio(trans, filename=filename)
        vc.play(discord.FFmpegPCMAudio(source=filename), after=print("Done"))
        while vc.is_playing():
            await asyncio.sleep(1)
        # await vc.disconnect()
    else:
        await ctx.send("not connected to VC")


@bot.command()
async def getLanguageCodes(ctx, *args):
    global blacklist
    auth = ctx.author
    if auth.name in blacklist:
        print("=================================================")
        print("Blacklisted user: ", auth.name)
        print("=================================================")
        return
    langcodes = ""
    for lang in constants.LANGCODES:
        langcodes = langcodes + lang + " -> " + constants.LANGCODES[lang] + "\t|\t"
    await ctx.send(langcodes)


@bot.command()
async def connectVoice(ctx, *args):
    global botVoiceChannel
    global blacklist
    auth = ctx.author
    if auth.name in blacklist:
        print("=================================================")
        print("Blacklisted user: ", auth.name)
        print("=================================================")
        return
    voiceChannel = auth.voice.channel
    if voiceChannel != None:
        vc = await voiceChannel.connect()
        botVoiceChannel = vc
    else:
        ctx.send("user not in VC")


@bot.command()
async def disconnectVoice(ctx, *args):
    global blacklist
    auth = ctx.author
    if auth.name in blacklist:
        print("=================================================")
        print("Blacklisted user: ", auth.name)
        print("=================================================")
        return
    global botVoiceChannel
    vc = botVoiceChannel
    await vc.disconnect()
    vc = 0


@bot.command()
async def updateBlacklist(ctx, *args):
    global blacklist
    auth = ctx.author
    if auth.name == operator:
        if args[0] == "add":
            blacklist.append(args[1])
        elif args[0] == "remove":
            blacklist.remove(args[1])
        print("new blacklist: ")
        print(blacklist)
    else:
        await ctx.send("You are not operator, talk to: " + operator)


def doTranslation(input, fromLang="en", toLang="pl"):
    return translator.translate(input, dest=toLang, src=fromLang)


def saveTranslationAudio(input, filename):
    txt = input.text
    toLang = input.dest
    audio = gTTS(text=txt, lang=toLang, slow=True)
    audio.save(filename)


def removeTranslationAudio(filename):
    os.remove(filename)


TOKEN = os.environ.get("TOKEN")
try:
    bot.run(TOKEN)
except discord.errors.LoginFailure as e:
    print("Login unsuccessful.")
    print(e)
