import discord
import asyncio
import datetime
import youtube_dl
import wordwolf as ww

client = discord.Client()


class Boss():

    def __init__(self, token):
        client.run(token)

    @client.event
    async def on_ready(self):
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')


token = ""
with open("token.txt") as f:
    token = f.read()
boss = Boss(token)
