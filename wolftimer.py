import discord
import asyncio
import datetime
import wordwolf as ww
client = discord.Client()

# 残り時間を知らせるタイミング
notice_time = [1,10, 30, 60, 120, 180, 240, 300, 420, 540]

force_break = False
given_time = 0
ql_time = 0

dm_address={}

w=ww.WordWolf()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    global force_break
    global given_time
    global ql_time
    force_break=False
    # 「おはよう」で始まるか調べる
    if message.content.startswith("おはよう"):
        # 送り主がBotだった場合反応したくないので
        if client.user != message.author:
            # メッセージを書きます
            m = "おはようございます" + message.author.name + "さん！"
            # メッセージが送られてきたチャンネルへメッセージを送ります
            # print(message.channel)
            await client.send_message(message.channel, m)

    #command parser
    args=["None"]
    argsize=0
    if message.content.startswith("!"):
        args=message.content.split(" ")
        args[0]=args[0][1:]
        argsize=len(args)
        print(args)

    if args[0] in ["reset"]:
        
        w.reset_player()
        m="リセットしました。\n参加するプレイヤーは !join を入力してください。\n!ww でゲームを開始します。"
        await client.send_message(message.channel, m)

    if args[0] in ["join"]:
        w.add_player(message.author.name)
        dm_address[message.author.name]=message.author
        m="参加を受け付けました。\n議論後はここで投票してね。\n参加を取り消す場合は !quit を入力してください。"
        print("players:",w.players)
        await client.send_message(message.author, m)

    if args[0] in ["quit"]:
        w.remove_player(message.author.name)
        m="参加を取り消しました。"
        print(w.players)
        await client.send_message(message.author, m)
    
    if args[0] in ["lobby"]:
        m="参加者: " +str(len(w.players))+ "人\n"
        for i in w.players:
            m+=i
            m+="\n"
        await client.send_message(message.channel, m)
    
    if args[0] in ["vote"]:
        if argsize<2:
            m="投票コマンドは !vote [相手のユーザー名] だよ。"
            await client.send_message(message.author, m)
        else:
            result=w.vote(message.author.name,args[1])
            if result!="OK":
                m="投票は受け付けられませんでした。\n"
                m+=result
                await client.send_message(message.author, m)
            else:
                m="投票を受け付けました。\n開票までなら変更することもできるよ。"
                await client.send_message(message.author, m)
    
    if args[0] in ["debug"]:
        m=w.get_info()
        await client.send_message(message.author, m)

    if args[0] in ["execute"]:
        execute(message.channel)

    if args[0] in ["seed"]:
        if argsize<2:
            m="シード値の指定は !seed [呪文] だよ。"
            await client.send_message(message.channel, m)
        try:
            w.set_seed(int(args[1]))
            m="シード値を "+args[1]+" に設定しました。"
            await client.send_message(message.channel, m)
        except Exception:
            w.set_seed(args[1])
            m="シード値を "+args[1]+" に設定しました。"
            await client.send_message(message.channel, m)
            

    if args[0] in ["wordwolf","ww"]:
        if len(w.players)==0:
            m = "参加者0人"
            await client.send_message(message.channel, m)
            return
        if client.user != message.author:
            given_time = 1
            if(argsize > 1):
                given_time = float(args[1])
            given_time *= 60
            m = "ワードウルフを始めます。\n議論の制限時間は" + str(int(given_time / 60)) + "分です。\nDMから自分のテーマを確認してね。"
            await client.send_message(message.channel, m)
            
            w.start()

            #テーマを伝える
            for i in w.players:
                info=w.get_info()
                print(info)
                if info["players"][i]["role"]=="wolf":
                    m="あなたは「"+info["game"]["theme"][1]+"」"
                else:
                    m="あなたは「"+info["game"]["theme"][0]+"」"
                await client.send_message(dm_address[i], m)


            m="参加者: " +str(len(w.players))+ "人\n"
            for i in w.players:
                m+=i
                m+="\n"
            await client.send_message(message.channel, m)

            end_time = loop.time() + given_time
            loop.call_soon(wordwolf, end_time, loop, message.channel)

    if message.content.startswith("!quizwolf") or message.content.startswith("!qw") or message.content.startswith("!ig"):
        if client.user != message.author:
            given_time = 1
            if(argsize > 1):
                given_time = float(args[1])
            given_time *= 60
            m = "インサイダーゲームを始めます。\n議論の制限時間は" + \
                str(int(given_time / 60)) + "分です。"
            end_time = loop.time() + given_time
            loop.call_soon(quizwolf, end_time, loop, message.channel)
            await client.send_message(message.channel, m)

    if args[0] in ["stop"]:
        force_break = True
        print(given_time, ql_time)
        m = "狼を当ててください。\n議論の制限時間は" + str(given_time - ql_time) + "秒です。"
        end_time = loop.time() + given_time - ql_time
        loop.call_later(2, wordwolf, end_time, loop, message.channel, [])
        await client.send_message(message.channel, m)

    if args[0] in ["kill"]:
        m = "実行中のゲームを終了しました"
        await client.send_message(message.channel, m)
        force_break = True

import time


async def send(channel, message):
    # print("called")
    await client.send_message(channel, message)
    # print("sent")



async def playing(txt):
    await client.change_presence(game=discord.Game(name=txt))


def execute(channel):
    global force_break
    force_break=True
    result,executed,role=w.execute()
    if result.startswith("Finish"):
        execute="処刑"
        m="投票の結果、" +executed+" さんが"+execute+"されました。\n"
        if role=="villager":
            m+=executed+" さんは多数派でした。よって、勝者は少数派である\n"
            for i in w.wolfs:
                m+=i
                m+=" さん\n"
            m+="に確定しました。"
        else:
            m+=executed+" さんは少数派でした。\n多数派のお題を言い当てれば逆転勝利だよ。（未実装）"
    elif result.startswith("Tie"):
        m="投票の結果、処刑対象を一人に絞れませんでした。\n最多得票者は\n"
        for i in executed:
            m+=i
            m+=" さん\n"
        m+="です。2分間の再議論の後、\nもう一度投票してください。"
        end_time = loop.time() + 120
        loop.call_later(2,wordwolf, end_time, loop, channel)
    else:
        force_break=False
        m="未投票の人がいます。"

    asyncio.ensure_future(send(channel,m))

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
