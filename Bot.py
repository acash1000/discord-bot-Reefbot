import time
import math
import discord
import youtube_dl
from discord.ext import commands
import os
from discord.utils import get
import shutil
import urllib.parse, urllib.request, re
from discord.ext.commands import bot
from os import system
queue_time = 0
client = commands.Bot(command_prefix='$')
players = {}
song_name: str = ""


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.command()
async def ping(ctx):
    await ctx.send(f'pong!! {round(client.latency * 1000)} ms')


@client.command()
async def clear(ctx, amount=10):
    await ctx.channel.purge(limit=amount)


@client.command()
async def kick(ctx, member: discord.member, reason=None):
    await member.kick(reason=reason)


@client.command()
async def ban(ctx, member: discord.member, reason=None):
    await member.ban(reason=reason)


@client.command()
async def unban(ctx, member):
    banned_users = await ctx.guild.bans()
    member_name, member_disc = member.split("#")
    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.disc) == (member_name, member_disc):
            await ctx.guild.unban(user)


@client.command()
async def join(ctx):
    try:
        channel = ctx.author.voice.channel
        await channel.connect()
    except AttributeError:
        await ctx.send("please join voice channel and try again")


@client.command()
async def leave(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_connected():
        await ctx.voice_client.disconnect()
        await ctx.send("Goodbye")
    else:
        await ctx.send("already gone")
    shutil.rmtree("./Queue")


@client.command()
async def play(ctx, *, input: str):
    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            name = os.path.basename(song_path)
            if length != 0:
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, "song.mp3")
                voice.play(discord.FFmpegPCMAudio("song.mp3"))
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07
                numname = name.split("g")[-1]
                nummname = numname.split(".")
                filename= nummname[0]
                f =open(f"./queue_directory/{filename}",'r')
                contents = f.read()
                ct = contents.split("-")[-1]
                foo = int(ct)
                foo1 = (foo%1)/60
                foo2 = (math.floor(foo)*60) +(foo1*60)
                queue_time - foo2
                os.remove(f"./queue_directory/{filename}")
            else:
                queues.clear()
                return
        else:
            queues.clear()

    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    if voice_client is None:
        try:
            channel = ctx.author.voice.channel
            await channel.connect()
        except AttributeError:
            await ctx.send("please join voice channel and try again")
    search = input.replace(" ", "-")
    query_string = urllib.parse.urlencode({
        'search_query': search
    })
    htm_content = urllib.request.urlopen(
        'http://www.youtube.com/results?' + query_string
    )
    search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())

    url = 'http://www.youtube.com/watch?v=' + search_results[0]
    if voice_client and voice_client.is_playing():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is False:
            os.mkdir("Queue")
        DIR = os.path.abspath(os.path.realpath("Queue"))
        q_num = len(os.listdir(DIR))
        q_num += 1
        add_queue = True
        while add_queue:
            if q_num in queues:
                q_num += 1
            else:
                add_queue = False
                queues[q_num] = q_num
        queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': queue_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("downloading audio now")
            ydl.download([url])
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
            duration = info_dict.get('duration', None)
        embed = discord.Embed(
            title=f"Queueing: {video_title}",
            Colour=discord.Colour.blue()
        )
        url2 = url.split("/")
        part = url2[-1].split("v=")[-1]
        embeddedurl = f"https://www.youtube.com/embed/{part}"
        embed.set_image(url=embeddedurl)
        time = duration / 60
        time2 = (time % 1)
        time3 = math.floor(time) + ((time2 * 60) * .01)
        embed.add_field(name="duration", value=f"{time3} minutes", inline=True)
        await ctx.send(embed=embed)
        await ctx.send(url)
        f = open(f"./queue_directory/{q_num}", "w+")
        f.write(f"{video_title}            -{time3} min")
        f.close()
        queue_time+duration
    else:
        song_there = os.path.isfile("song.mp3")

        try:
            if song_there:
                os.remove("song.mp3")
                song_name = ""
                queues.clear()
                print("removed old song file")
        except PermissionError:
            print("trying to delete, but it it is being played")
            await ctx.send("ERROR music is playing")
            return
        Queue_infile = os.path.isdir("./Queue")
        try:
            Queue_folder = "./Queue"
            if Queue_infile is True:
                shutil.rntree(Queue_folder)
        except:
            print("not queue")
        await ctx.send("getting everything ready")
        voice = get(client.voice_clients, guild=ctx.guild)
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("downloading audio now")
            ydl.download([url])
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
            duration = info_dict.get('duration', None)
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                name = file
                print(f"renamed file{file}")
                os.rename(file, "song.mp3")
        voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 0.07
        nname = name.rsplit("-", 2)
        embed = discord.Embed(
            title=f"Playing: {video_title}",
            Colour=discord.Colour.blue()
        )
        url2 = url.split("/")
        part = url2[-1].split("v=")[-1]
        embeddedurl = f"https://www.youtube.com/embed/{part}"
        embed.set_image(url=embeddedurl)
        time = duration / 60
        time2 = (time % 1)
        time3 = math.floor(time) + ((time2 * 60) * .01)
        embed.add_field(name="duration", value=f"{time3} minutes", inline=True)
        await ctx.send(embed=embed)
        await ctx.send(url)
        print("playing")


@client.command(aliases=["p"])
async def pause(ctx):
    voice = get(ctx.bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        voice.pause()
        await ctx.send("pause")
    else:
        await ctx.send("nothing be playing bro")


@client.command(aliases=["r"])
async def resume(ctx):
    voice = get(ctx.bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        voice.resume()
        await ctx.send(f"{song_name} is resumed")
    else:
        ctx.send("music is not paused, keep listening")


@client.command()
async def stop(ctx):
    voice = get(ctx.bot.voice_clients, guild=ctx.guild)

    queues.clear()
    queue_infile = os.path.isdir("./Queue")
    if queue_infile is True:
        shutil.rmtree("./Queue")
    if voice and voice.is_playing():
        voice.stop()
        await ctx.send("stopped")
    else:
        await ctx.send("nothing be playing bro")


queues = {}


@client.command(aliases=["s"])
async def skip(ctx):
    voice = get(ctx.bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.stop()
        await ctx.send("next song")
    else:
        await ctx.send("nothing be playing bro")


@client.command(aliases =["q"])
async def queue(ctx):
    DIR = os.path.abspath(os.path.realpath("queue_directory"))
    length = len(os.listdir(DIR))
    queuess = []
    if length != 0:
        for file in os.listdir(DIR):
            tfile =open(f"./queue_directory/{file}", 'r')
            contents = tfile.read()
            queuess.append(contents)
        embed = discord.Embed(
            title="queue",
            colour= discord.Colour.blue()
        )
        for x in queuess:
            embed.add_field(name="song",value= x,inline=True)
    time = queue_time / 60
    time2 = (time % 1)
    time3 = math.floor(time) + ((time2 * 60) * .01)
    embed.add_field(name="time",value= str(time3),inline=False)
    await ctx.send(embed=embed)

@client.command()
async def youtube(ctx, *, search: str):
    query_string = urllib.parse.urlencode({
        'search_query': search
    })
    htm_content = urllib.request.urlopen(
        'http://www.youtube.com/results?' + query_string
    )
    search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())

    await ctx.send('http://www.youtube.com/watch?v=' + search_results[0])


@client.command(aliases=["ab"])
async def anbublackops(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    if voice_client is None:
        try:
            channel = ctx.author.voice.channel
            await channel.connect()
        except AttributeError:
            await ctx.send("please join voice channel and try again")
    voice = get(ctx.bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.stop()
    else:
        print("i")
    source = discord.FFmpegPCMAudio('troll.m4a')
    voice.play(source)
    while voice.is_playing():
        time.sleep(1)
    source = discord.FFmpegPCMAudio("./anbu/anbuTROLLOLOLOL.mp3")
    voice.play(source)
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.05
    while voice.is_playing():
        time.sleep(1)
    await voice.disconnect()
    user = 271109260518227969
    member = discord.Guild.get_member(ctx.guild, user)
    reason = None
    await member.kick(reason=reason)


client.run("NzM5MDM1OTE4NTg1MDM2ODMx.XyUm1Q.a6C2EdovlCK8ZeaXAqthOSjNVU0")
