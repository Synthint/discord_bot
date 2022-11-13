import discord
from discord.ext import commands
import os
from googletrans import Translator, constants
import dotenv
import speech_recognition
from gtts import gTTS
import asyncio
import speech_recognition
from struct import pack, unpack



dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)
global blacklist
global botVoiceChannel
global operator
botVoiceChannel = 0
blacklist = os.environ.get("BLACKLIST").split(",")
operator = os.environ.get("OP")
translator = Translator()
recognizer = speech_recognition.Recognizer()


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix=">", intents=intents)


@bot.command()
async def translate_text(ctx, *args):
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
async def translate_voice(ctx, *args):
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
async def get_langs(ctx, *args):
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
async def connect_voice(ctx, *args):
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
async def disconnect_voice(ctx, *args):
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
async def update_blacklist(ctx, *args):
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


"""




"""

def saveAudio(aud,fileName):
    with open(fileName,"wb") as f:
        f.write(aud.getbuffer())
    f.close


def repairAudio(filename):
    wav_header = "4si4s4sihhiihh4si"

    f = open(filename, 'rb+')
    data = list(unpack(wav_header,f.read(44)))
    assert data[0]=='RIFF'
    assert data[2]=='WAVE'
    assert data[3]=='fmt '
    assert data[4]==16
    assert data[-2]=='data'
    assert data[1]==data[-1]+36

    f.seek(0,2)
    filesize = f.tell()
    datasize = filesize - 44

    data[-1] = datasize
    data[1]  = datasize+36

    f.seek(0)
    f.write(pack(wav_header, *data))
    f.close()


async def once_done(sink: discord.sinks, channel: discord.TextChannel, *args):  
    files = [
        discord.File(audio.file, f"{user_id}.{sink.encoding}") 
        for user_id, audio in sink.audio_data.items()
        ]
    print("\n\n\n")
    print(files[0])
    print("\n\n\n")
    for user_id, audio in sink.audio_data.items():
        print(audio.file)
        print(type(audio))
        print(user_id)
        saveAudio(audio.file,str(user_id)+".wav")
        repairAudio(str(user_id)+".wav")

    with speech_recognition.AudioFile("400001737911697408.wav") as source:
        audioData = recognizer.record(source)
    print(type(audioData))
    text = recognizer.recognize_google(audioData,language="en",show_all=True)
    print("Transcription:" ,  text["alternative"][0]["transcript"])
    print(type(text))

    #await channel.send(f"finished recording audio for: {', '.join(recorded_users)}.", files=files)  

@bot.command()
async def record(ctx):  # If you're using commands.Bot, this will also work.
    voice = ctx.author.voice

    if not voice:
        await ctx.send("You aren't in a voice channel!")
    global botVoiceChannel
    vc = botVoiceChannel
    vc.start_recording(
        discord.sinks.WaveSink(),  # The sink type to use.
        once_done,  # What to do once done.
        ctx.channel  # The channel to disconnect from.
    )
    await ctx.send("Started recording!")

@bot.command()
async def stop_recording(ctx):
    global botVoiceChannel
    vc = botVoiceChannel
    vc.stop_recording()  # Stop recording, and call the callback (once_done).

"""




"""


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
