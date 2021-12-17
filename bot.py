from discord.ext import commands
from youtube_dl import YoutubeDL
import discord

#префикс можно поставить абсолютно любой, какой нравится
bot = commands.Bot(command_prefix='!')

#отправляет команду !help в текстовый канал при запуске бота
bot.remove_command('help')

class general_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = """
```
Главные команды:
!help - показывает все доступные команды
!clear <n> - удаляет n последних сообщений на канале

Музыкальные команды:
!p(lay) <keywords> - находит трек в YouTube и воспроизводит его
!n(ext) - воспроизводит следующий трек из очереди
!q(ueue) - показывает очередь треков, которые будут воспроизводиться
!ps(pause) - ставит трек на паузу
!r(esume) - снимает трек с паузы
!dt(disconnect) - отключает бота от голосового канала
```
"""
        self.text_channel_list = []

    #некоторая отладочная информация, чтобы мы знали, что бот запустился
    @commands.Cog.listener()
    async def on_ready(self):
        '''
        асинхонная функция, запускающаяся, когда запускается бот.
        class disord.commands - класс discord.py, представляющий собой клиентское соединение, которое подключается к Discord
        '''
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_list.append(channel)

        await self.send_to_all(self.help_message)


    @commands.command(name="help", help="показывает все доступные команды")
    async def help(self, ctx):
        '''
        функция для показа доступных реалтзованных команд
        аргумент ctx - контекст
        '''
        await ctx.send(self.help_message)
        return self.help_message

    async def send_to_all(self, msg):
        for text_channel in self.text_channel_list:
            await text_channel.send(msg)

    @commands.command(name="clear", help="удаляет n последних сообщений")
    async def clear(self, ctx, arg):
        '''
        функция для очистки чата
        аргумент ctx - контекст
        аргумент amount : int - количсетво желаемых удаленных сообщений, с последнего отправленного
        '''
        amount = 5
        try:
            amount = int(arg)
        except Exception:
            pass
        await ctx.channel.purge(limit=amount)
        await ctx.send('```я удалил эти бесполезные сообщения```')

class music_cog(commands.Cog):
    # дефолтные настройки для того, чтобы понять, что делает бот
    def __init__(self, bot):
        self.bot = bot
        # играет музыка в настоящее время или нет
        self.is_playing = False
        # данный массив отслеживает, какая музыка находится в очереди и на каком канале
        self.music_queue = []
        # настройки для лучшего качества воспроизведения треков (данные настройки можно найти в библиотеках)
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}
        self.vc = ""

    def search_yt(self, item):
        '''
        функция для поиска трека на YouTube
        '''
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:
                return False
        # сохраняем информацию о треке, то есть его URl-адрес и название, чтобы потом добавить в очередь
        return {'source': info['formats'][0]['url'], 'title': info['title']}
    #----------------Взаимствованная часть кода----------------# (немного переделанная)
    # как только бот закончит играть первую песню, сразу начнёт играть следующая, если в очереди что-то есть
    def play_next(self):
        '''
        функция для впоспоизведения треков по очереди
        '''
        # проверяем есть ли в массиве очереди треки
        if len(self.music_queue) > 0:
            self.is_playing = True
            # получаем первый url адрес
            m_url = self.music_queue[0][0]['source']
            # удаляем первый элемент массива очереди с треками
            self.music_queue.pop(0)
            # данная часть кода "after=lambda e: self.play_next()" позволяет рекурсивно возвращаться к началу очереди и проверять, есть ли далее трек
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            # проверяем подключены ли мы к головому каналу
            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])
            print(self.music_queue)
            # удаляем первый элемент массива очереди с треками
            self.music_queue.pop(0)
            # данная часть кода "after=lambda e: self.play_next()" позволяет рекурсивно возвращаться к началу очереди и проверять, есть ли далее трек
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False
        # ctx нужен для того, что понять с какого чата пользователь послал сообщение и чтобы понять, к какому голосовому каналу нужно присоединиться
    #------------------------------------------------------------------------------------------------------------------------------------------------#

    @commands.command(name="p", help="находит трек в YouTube и воспроизводит его")
    async def play(self, ctx, *args):
        '''
        функция для воспроизведения трека
        '''
        # преобразовываем аргументы в строку
        query = " ".join(args)
        # сохраняем голосовой канал с которого пользователь отправлял сообщение
        voice_channel = ctx.author.voice.channel
        # если голосового канала не найдено
        if voice_channel is None:
            # you need to be connected so that the bot knows where to go
            await ctx.send("```присоеденись с голосовому каналу```")
        else:
            # если пользователь дейстительно подключён, то ищем в YouTube трек, который пользователь хочет воспроизвести
            song = self.search_yt(query)
            await ctx.send("```добавил трек в очередь```")
            self.music_queue.append([song, voice_channel])
            # если музыка не играет
            if self.is_playing == False:
                await self.play_music()

    @commands.command(name="q", help="отправляет очередь треков, которые будут воспроизводиться")
    async def queue(self, ctx):
        '''
        функция для отправки очереди в чат
        '''
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += self.music_queue[i][0]['title'] + "\n"

        print(retval)
        # если в очереди действительно что-то есть, то мы отправялем очередь на канал, иначе возвращаем "нет треков в очереди"
        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("```нет треков в очереди```")

    @commands.command(name="n", help="воспроизводит следующий трек из очереди")
    async def next(self, ctx):
        '''
        функция для включния следующего трека
        '''
        # убеждаемся, что бот подключен к головому каналу
        if self.vc != "" and self.vc:
            self.vc.stop()
            # пробует играть следующий трек из очереди
            await self.play_music()
            await ctx.send("```ладно, послушаем следующиий трек```")

    @commands.command(name="ps", help="ставит трек на паузу")
    async def pause(self, ctx):
        '''
        функция для того, чтобы поставить трек на паузу
        '''
        vc = ctx.voice_client
        vc.pause()
        await ctx.send("```поставил трек на паузу```")

    @commands.command(name="r", help="снимает трек с паузы")
    async def resume(self, ctx):
        '''
        функция для того, чтобы снять трек с паузы
        '''
        vc = ctx.voice_client
        vc.resume()
        await ctx.send("```снял трек с паузы```")

    @commands.command(name="dt", help="отключает бота от голосового канала")
    async def disconnect(self, ctx):
        '''
        функция для отключения бота от голсового канала
        '''
        await self.vc.disconnect()
        await ctx.send("```до скорых встреч```")
def BotAnswer(UserData):
    x = 'Цепи Скриптонит'
    UserSent = {
        '!start': 'Ку) Я mu$icant - бот, которого ты ещё не видел нигде! Чувак, да, я бот, но мой скилл покруче живых, поверь XD. \nКороче не будем медлить. Держи мой IQ наборчик: \n!help - если вдруг забыл как мной пользоваться)) \n!p - поставлю музычку на любой вкус \n!ps - тормознем трек \n!n - воспроизведу следующий трек \n!clear - удалю эти бесполезные сообщения',
        '!help': 'Давай-ка напомню тебе) \n!p - поставлю музычку на любой вкус \n!ps - тормознем трек \n!n - воспроизведу следующий трек \n!clear - удалю эти бесполезные сообщения',
        '!p': 'Запустил трек ' + '"' + x + '"',
        '!ps': 'Так так так, ставлю на паузу!',
        '!n': 'Воспроизвёл следующий трек ' + '"' + x + '"',
        '!clear': 'Удалил эти бесполезные сообщения!'
    }
    BotOtvet = ''
    if UserData == '!start':
        BotOtvet = UserSent['!start']
    elif UserData == '!help':
        BotOtvet = UserSent['!help']
    elif UserData == '!p':
        BotOtvet = UserSent['!p']
    elif UserData == '!ps':
        BotOtvet = UserSent['!ps']
    elif UserData == '!n':
        BotOtvet = UserSent['!n']
    elif UserData == '!clear':
        BotOtvet = UserSent['!clear']
    else:
        BotOtvet = 'Пока не научился отвечать на такое'
    return BotOtvet

#добавляем функции из файлов проекта
bot.add_cog(general_cog(bot))
bot.add_cog(music_cog(bot))

#заупскаем нашего бота, для этого нужен токен бота, который можно посмотреть на сайте discord.developers
bot.run("OTEwODcwMDA5MTU5NTA3OTg4.YZZHzQ.laM95CpDOEGNMUeLYkXv2C3-Kw0")
