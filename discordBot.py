
import discord
from discord.ext import commands
import os
from googletrans import Translator, constants
from dotenv import load_dotenv
import speech_recognition
from gtts import gTTS
import asyncio
load_dotenv()


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!',intents=intents)
translator = Translator()


@bot.command()
async def textTranslate(ctx,*args):
    auth = ctx.author
    args = list(args)
    if len(args) == 1:
        args.append("en")
    if len(args) == 2:
        args.append("pl")
    await ctx.send(doTranslation(input=args[0],fromLang = args[1],toLang=args[2]).text)
    


@bot.command()
async def voiceTranslate(ctx,*args):
    auth = ctx.author
    voiceChannel = auth.voice.channel
    if voiceChannel != None:
        args = list(args)
        if len(args) == 1:
            args.append("en")
        if len(args) == 2:
            args.append("pl")
        print(args)
        trans = doTranslation(input=args[0],fromLang = args[1],toLang=args[2])
        
        vc = await voiceChannel.connect()
        filename = "tempTranslation.mp3"
        saveTranslationAudio(trans,filename=filename)
        print(vc)
        vc.play(discord.FFmpegPCMAudio(source=filename), after=print("Done"))
        while not vc.is_playing():
            await asyncio.sleep(1)
        await vc.disconnect
    else:
        ctx.send("user not in VC")


def doTranslation(input,fromLang="en",toLang="pl"):
    print("++++ TRANSLATION WANTED ++++")
    print(input)
    print(fromLang)
    print(toLang)
    print("============================")
    return translator.translate(input,dest = toLang,src=fromLang)

def saveTranslationAudio(input, filename = "tempTranslation.mp3"):
    txt = input.text
    toLang = input.dest
    audio = gTTS(text = txt,lang = toLang,slow=True)
    audio.save(filename)

def removeTranslationAudio(filename ="tempTranslation.mp3"):
    os.remove(filename)

TOKEN = os.environ.get('TOKEN')
try:
    bot.run(TOKEN)
except discord.errors.LoginFailure as e:
    print("Login unsuccessful.")
    print(e)