import discord
import asyncio
import datetime
import youtube_dl
import wordwolf as ww

client = discord.Client()


class Boss():

    def __init__(self, token):
        client.run(token)

    async def on_ready(self):
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

    async def on_message(message):
        global force_break
        global given_time
        global ql_time
        global game_channel
        force_break = False
        # 「おはよう」で始まるか調べる
        if message.content.startswith("おはよう"):
            # 送り主がBotだった場合反応したくないので
            if client.user != message.author:
                # メッセージを書きます
                m = "おはようございます" + message.author.name + "さん！"
                # メッセージが送られてきたチャンネルへメッセージを送ります
                # print(message.channel)
                await client.send_message(message.channel, m)


@client.event
async def on_ready(self):
    boss.on_ready()


@client.event
async def on_message(message):
    boss.on_message(message)


token = ""
with open("token.txt") as f:
    token = f.read()
boss = Boss(token)
