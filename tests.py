from bot import BotAnswer
import unittest
x = 'Цепи Скриптонит'

class BotExam(unittest.TestCase):
    def testPause(self):
        self.assertEqual(BotAnswer('!ps'), 'Так так так, ставлю на паузу!')

    def testStart(self):
        self.assertEqual(BotAnswer('!start'), 'Ку) Я mu$icant - бот, которого ты ещё не видел нигде! Чувак, да, я бот, но мой скилл покруче живых, поверь XD. \nКороче не будем медлить. Держи мой IQ наборчик: \n!help - если вдруг забыл как мной пользоваться)) \n!p - поставлю музычку на любой вкус \n!ps - тормознем трек \n!n - воспроизведу следующий трек \n!clear - удалю эти бесполезные сообщения')

    def testHelp(self):
        self.assertEqual(BotAnswer('!help'), 'Давай-ка напомню тебе) \n!p - поставлю музычку на любой вкус \n!ps - тормознем трек \n!n - воспроизведу следующий трек \n!clear - удалю эти бесполезные сообщения')

    def testSkip(self):
        self.assertEqual(BotAnswer('!n'), 'Воспроизвёл следующий трек ' + '"' + x + '"')

    def testClear(self):
        self.assertEqual(BotAnswer('!clear'), 'Удалил эти бесполезные сообщения!')

    def testPlay(self):
        self.assertEqual(BotAnswer('!p'), 'Запустил трек ' + '"' + x + '"')
