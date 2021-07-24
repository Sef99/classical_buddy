import discord
from decouple import config
from discord.ext import commands
from clcomposer_api import *
import random
from youtube_dl import YoutubeDL

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist':'True'}

bot = commands.Bot(command_prefix='!')

async def process_composer(ctx, composer_details):
    if await composer_existence(ctx, composer_details):
        for composers in composer_details['composers']:
                wikipedia_desc = wikiapi(composers["complete_name"])
                sep = '\n'
                pageid = wikipedia_desc['query']['pageids'][0]
                stripped = wikipedia_desc['query']['pages'][str(pageid)]['extract'].split(sep, 1)[0]
                embed_message = discord.Embed(title=composers["complete_name"], description=stripped, color=discord.Color.orange())
                embed_message.set_image(url="http" + composers["portrait"][5:])
                await ctx.channel.send(embed=embed_message)

async def composer_existence(ctx, composer_details):
    if composer_details['status']['success'] == 'false':
        await ctx.channel.send("We have not found your requested composer in our database.")
        return False
    return True

def process_works(composer_details):
    composer_id = composer_details['composers'][0]['id']
    work_details = get_workdet(composer_id)
    return work_details

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_guild_join(guild):
    for general in guild.text_channels:
        if general and general.permissions_for(guild.me).send_messages:
            await general.send('Thanks for adding me to your lovely server! Please use the command !info to understand how to use me.')
            return

@bot.command(name='info')
async def _help(ctx):
    embed_message = discord.Embed(title = 'Available Commands: ')
    embed_message.add_field(name='!desc composer', value='Returns a brief description of the composer.', inline=False)
    embed_message.add_field(name='!random', value='Returns a brief description of a random composer.', inline=False)
    embed_message.add_field(name='!works composer', value='Returns a list of recommended works of the composer.', inline=False)
    embed_message.add_field(name='!rec composer', value='Recommends and plays a random piece from the given composer. \nTo pause and resume: !pause and !resume.\nTo make the bot leave the channel: !leave', inline=False)
    await ctx.send(embed=embed_message)

@bot.command(name='desc')
async def _search_name(ctx, composer_name):
    composer_details = get_composerdet(composer_name)
    await process_composer(ctx, composer_details)

@bot.command(name='random')
async def _search_random(ctx):
    composer_details = get_random()
    wikipedia_desc = wikiapi(composer_details['composers'][0]['complete_name'])
    await process_composer(ctx, composer_details)

@bot.command(name='works')
async def _search_works(ctx, composer_name):
    composer_details = get_composerdet(composer_name)
    if await composer_existence(ctx, composer_details):
        work_details = process_works(composer_details)
        embed_message = discord.Embed(title='Works by: ' + work_details['composer']['complete_name'], color=discord.Color.orange())
        embed_message.set_thumbnail(url="http" + composer_details['composers'][0]['portrait'][5:])
        for works in work_details['works']:
            embed_message.add_field(name='Title: ', value=works['title'], inline=False)
            embed_message.add_field(name='Genre: ', value=works['genre'], inline=True)
        await ctx.channel.send(embed=embed_message)

@bot.command(name='rec')
async def _rec_works(ctx, composer_name):
    composer_details = get_composerdet(composer_name)
    if await composer_existence(ctx, composer_details):
        work_details = process_works(composer_details)
        works_num = len(work_details['works'])
        ran_num = random.randrange(0, works_num, 1)
        title = work_details['works'][ran_num]['title']
        yt_det = yt_api(title)
        video_id = yt_det['items'][0]['id']['videoId']
        if ctx.message.author.voice == None:
            await ctx.channel.send("Please connect to a Voice Channel")
            return
        else:
            embed_message = discord.Embed(title=composer_details['composers'][0]['complete_name'], description=title, color=discord.Color.orange())
            await ctx.send(embed=embed_message)
            await _play_video(ctx, video_id)

#needs only the video id of a youtube video, rather than the full url, in order to work. i.e. !p DZTAXk2NOdc
@bot.command(name='p')
async def _play_video(ctx, video_id):
    bot_vc = ctx.voice_client
    if not bot_vc or not bot_vc.is_connected():
        vc = ctx.author.voice.channel
        await vc.connect()
    voice = ctx.voice_client
    url = 'https://www.youtube.com/watch?v=' + video_id
    info = YoutubeDL(YDL_OPTIONS).extract_info(url, download=False)
    iurl = info['formats'][0]['url']
    source = await discord.FFmpegOpusAudio.from_probe(iurl, **FFMPEG_OPTIONS)
    if not voice.is_playing():
        voice.play(source)
    else:
        voice.stop()
        voice.play(source)

@bot.command(name='pause')
async def _pause(ctx):
    vc = ctx.voice_client
    if not vc or not vc.is_playing():
        await ctx.send('I am currently not playing anything')
    elif vc.is_paused():
        return
    vc.pause()
    await ctx.send('Paused')

@bot.command(name='resume')
async def _resume(ctx):
    vc = ctx.voice_client
    if not vc or not vc.is_connected():
        await ctx.send('I am currently not in a voice channel')
    elif not vc.is_paused():
        return
    vc.resume()
    await ctx.send('Resuming')

@bot.command(name='leave')
async def _disconnect(ctx):
    await ctx.voice_client.disconnect()

bot.run(config('BOT_KEY'))