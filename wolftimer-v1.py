import discord
import asyncio
import datetime

client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    # 「おはよう」で始まるか調べる
    if message.content.startswith("おはよう"):
        # 送り主がBotだった場合反応したくないので
        if client.user != message.author:
            # メッセージを書きます
            m = "おはようございます" + message.author.name + "さん！"
            # メッセージが送られてきたチャンネルへメッセージを送ります
            # print(message.channel)
            await client.send_message(message.channel, m)

    if message.content.startswith("!wordwolf") or message.content.startswith("!ww"):
        if client.user != message.author:
            args = message.content.split(" ")
            argsize = len(args)
            given_time = 1
            if(argsize > 1):
                given_time = float(args[1])
            given_time = given_time * 60
            m = "ワードウルフを始めます。\n議論の制限時間は" + str(int(given_time / 60)) + "分です。"
            end_time = loop.time() + given_time
            loop.call_soon(wordwolf, end_time, loop, message.channel)
            await client.send_message(message.channel, m)

    if message.content.startswith("!quizwolf") or message.content.startswith("!qw") or message.content.startswith("!ig"):
        if client.user != message.author:
            args = message.content.split(" ")
            argsize = len(args)
            global given_time
            given_time = 1
            if(argsize > 1):
                given_time = float(args[1])
            given_time = given_time * 60
            m = "インサイダーゲームを始めます。\n議論の制限時間は" + \
                str(int(given_time / 60)) + "分です。"
            end_time = loop.time() + given_time
            loop.call_soon(quizwolf, end_time, loop, message.channel)
            await client.send_message(message.channel, m)

    if message.content.startswith("!stop"):
        global force_break
        global given_time
        global ql_time
        force_break = True
        print(given_time, ql_time)
        m = "狼を当ててください。\n議論の制限時間は" + str(given_time - ql_time) + "秒です。"
        end_time = loop.time() + given_time - ql_time
        loop.call_later(2, wordwolf, end_time, loop, message.channel, [])
        await client.send_message(message.channel, m)

    if message.content.startswith("!kill"):
        m = "実行中のゲームを終了しました"
        await client.send_message(message.channel, m)
        global force_break
        force_break = True

import time


async def send(channel, message):
    # print("called")
    await client.send_message(channel, message)
    # print("sent")


async def playing(txt):
    await client.change_presence(game=discord.Game(name=txt))


# 残り時間を知らせるタイミング
notice_time = [10, 30, 60, 120, 180, 240, 300, 420, 540]

force_break = False
given_time = 0
ql_time = 0


def quizwolf(end_time, loop, message_channel, precaution_time=None):
    left_time = end_time - loop.time()
    print(datetime.datetime.now(), left_time, "remaining")

    global force_break
    if force_break == True:
        force_break = False
        asyncio.ensure_future(playing(""))
        global ql_time
        ql_time = left_time
        print("ql assigned to", ql_time)
        return
    # 初回起動時
    if precaution_time == None:
        # 警告時刻の設定
        precaution_time = []
        for i in notice_time:
            if loop.time() > end_time - i:
                break
            # print(end_time, i)
            # print(precaution_time, type(precaution_time))
            # print(end_time)
            precaution_time.append(end_time - i)

    if(loop.time() + 1.0) < end_time:
        try:
            # 1秒ごとに呼ぶ
            loop.call_later(1, wordwolf, end_time, loop,
                            message_channel, precaution_time)

            # 5秒ごとに呼ぶ
            if(int(left_time) % 5 == 0):
                asyncio.ensure_future(
                    playing("あと" + str(int(left_time)) + "秒: クイズウルフ"))

            if precaution_time == []:
                pass
            # 残りN秒で呼ぶ
            elif precaution_time[-1] < loop.time() + 1.0:
                if left_time > 60:
                    m = "残り" + str(int(left_time / 60)) + "分です。"
                elif left_time >= 10:
                    m = "残り" + str(int(left_time)) + "秒です。"
                else:
                    #m = str(int(left_time))
                    m = "残り" + str(int(left_time)) + "秒です。"
                print(m)
                print("message_channel", message_channel)
                # client.send_message(message_channel, m)
                asyncio.ensure_future(send(message_channel, m))
                # c = asyncio.get_event_loop()
                # c.call_soon(send, message_channel, m)
                # c.run_once()
                del precaution_time[-1]

        except KeyError:
            print("Unknown error. timer stopped.")
            # loop.call_soon(loop.stop)

    else:
        print("time is over!")
        m = "制限時間を過ぎました。\n投票に移ってください。"
        asyncio.ensure_future(playing(""))
        asyncio.ensure_future(send(message_channel, m))
        loop.call_soon(loop.stop)  # 単に loop.stop() でもいい


def wordwolf(end_time, loop, message_channel, precaution_time=None):
    left_time = end_time - loop.time()
    print(datetime.datetime.now(), left_time, "remaining")

    global force_break
    if force_break == True:
        force_break = False
        asyncio.ensure_future(playing(""))
        return

    # 初回起動時
    if precaution_time == None:
        # 警告時刻の設定
        precaution_time = []
        for i in notice_time:
            if loop.time() > end_time - i:
                break
            # print(end_time, i)
            # print(precaution_time, type(precaution_time))
            # print(end_time)
            precaution_time.append(end_time - i)

    if(loop.time() + 1.0) < end_time:
        try:
            # 1秒ごとに呼ぶ
            loop.call_later(1, wordwolf, end_time, loop,
                            message_channel, precaution_time)

            # 5秒ごとに呼ぶ
            if(int(left_time) % 5 == 0):
                asyncio.ensure_future(
                    playing("あと" + str(int(left_time)) + "秒 : ワードウルフ"))

            if precaution_time == []:
                pass
            # 残りN秒で呼ぶ
            elif precaution_time[-1] < loop.time() + 1.0:
                if left_time > 60:
                    m = "残り" + str(int(left_time / 60)) + "分です。"
                elif left_time >= 10:
                    m = "残り" + str(int(left_time)) + "秒です。"
                else:
                    m = str(int(left_time))
                print(m)
                print("message_channel", message_channel)
                # client.send_message(message_channel, m)
                asyncio.ensure_future(send(message_channel, m))
                # c = asyncio.get_event_loop()
                # c.call_soon(send, message_channel, m)
                # c.run_once()
                del precaution_time[-1]

        except KeyError:
            print("Unknown error. timer stopped.")
            loop.call_soon(loop.stop)

    else:
        print("time is over!")
        asyncio.ensure_future(playing(""))
        m = "制限時間を過ぎました。\n投票に移ってください。"
        asyncio.ensure_future(send(message_channel, m))
        # loop.call_soon(loop.stop)  # 単に loop.stop() でもいい


loop = asyncio.get_event_loop()

# Schedule the first call to wordwolf()
#end_time = loop.time() + 5.0
# loop.call_soon(wordwolf, end_time, loop)

# Blocking call interrupted by loop.stop()
# loop.run_forever()
# loop.close()

# token にDiscordのデベロッパサイトで取得したトークンを入れてください
client.run("NDYzNjMzNjk5Mzg1MTE0NjI0.Dh0UdA.DnYYeJmy7Rrywcjc9KTxnjAAvwM")
