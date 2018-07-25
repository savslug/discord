import discord
import asyncio
import datetime
import wordwolf as ww
client = discord.Client()

# 残り時間を知らせるタイミング
notice_time = [1, 10, 30, 60, 120, 180, 240, 300, 420, 540]

force_break = False
given_time = 0
ql_time = 0
# ゲームが開催されているチャンネルを保存
game_channel = None

dm_address = {}

w = ww.WordWolf()

voice = None
bgm = None


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
    global game_channel
    global voice
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

    # command parser
    args = ["None"]
    argsize = 0
    if message.content.startswith("!"):
        args = message.content.split(" ")
        args[0] = args[0][1:]
        argsize = len(args)
        print(args)

    if args[0] in ["help"]:
        m = "使い方を検索中...検索中...\n"
        f = open('help.txt')
        data = f.read()  # ファイル終端まで全て読んだデータを返す
        f.close()
        # print(data)  # 文字列データ
        m += data
        await client.send_message(message.channel, m)

    # 音声関連
    if args[0] in ["voice", "boss"]:
        for channel in message.server.channels:
            if message.author in channel.voice_members:
                # voice使用者のいるチャンネルを発見
                voice = await client.join_voice_channel(channel)
                m = "ボイス機能をオンにしました。終了する場合は !bye だよ。"
                await client.send_message(message.channel, m)
                return
        else:
            m = "ボイス機能を使用するボイスチャンネルに入ってから呼んでね。"
            await client.send_message(message.channel, m)

    if args[0] in ["bye"]:
        try:
            await voice.disconnect()
            voice = None
            print(type(voice))
        except Exception:
            m = "ｱﾜﾜﾜﾜ...(既にボイスチャンネルを離れています)"
            await client.send_message(message.channel, m)

    if args[0] in ["youtube"]:
        global bgm
        if argsize < 2:
            bgm.stop()
            bgm = None
            m = "再生を停止しました。\nyoutubeの動画の音声を再生するには !youtube [動画URL] だよ。"
            await client.send_message(message.channel, m)
            return
        if voice == None:
            m = "!voice でボイス機能をオンラインにしてから使ってね。"
            await client.send_message(message.channel, m)
            return
        if bgm != None:
            bgm.stop()
            bgm = None
        m = "停止する場合は !youtube だよ。\n動画音声の再生準備中... "
        await client.send_message(message.channel, m)
        bgm = await voice.create_ytdl_player(args[1])
        bgm.start()

    if args[0] in ["reset"]:
        if w.state != "accepting_player":
            m = "そのコマンドは参加者受付中にしか実行できないよ。"
            await client.send_message(message.channel, m)
            return

        w.reset_player()
        m = "リセットしました。\n参加するプレイヤーは !join を入力してください。\n!ww でゲームを開始します。"
        await client.send_message(message.channel, m)

    if args[0] in ["join"]:
        if w.state != "accepting_player":
            m = "そのコマンドは参加者受付中にしか実行できないよ。"
            await client.send_message(message.channel, m)
            return
        w.add_player(message.author.name)
        dm_address[message.author.name] = message.author
        m = "参加を受け付けました。\n議論後はここで投票してね。\n参加を取り消す場合は !quit を入力してください。"
        print("players:", w.players)
        await client.send_message(message.author, m)

    if args[0] in ["quit"]:
        if w.state != "accepting_player":
            m = "そのコマンドは参加者受付中にしか実行できないよ。"
            await client.send_message(message.channel, m)
            return
        w.remove_player(message.author.name)
        m = "参加を取り消しました。"
        print(w.players)
        await client.send_message(message.author, m)

    if args[0] in ["lobby"]:

        m = "シード:" + str(w.seed) + "\n狼人数:" + str(w.wolf_size) + "\n"
        m += "参加者: " + str(len(w.players)) + "\n"
        for i in w.players:
            m += i
            m += "\n"
        await client.send_message(message.channel, m)

    if args[0] in ["vote"]:
        if w.state != "theme_discussion":
            m = "そのコマンドはゲーム中にしか実行できないよ。"
            if args[1] in ["felmac"] or nickname(args[1]) in ["felmac"]:
                m = message.author.name+"を処刑しました。BANポイントが1点加算されます。"
            await client.send_message(message.channel, m)
            return
        if argsize < 2:
            m = "投票コマンドは !vote [相手のユーザー名] だよ。"
            await client.send_message(message.author, m)
        else:
            # プレイヤーの中に存在しない投票先だった場合、
            # ニックネーム辞書を使ってみる
            if args[1] not in w.players:
                args[1] = nickname(args[1])

            result = w.vote(message.author.name, args[1])
            if result != "OK":
                m = "投票は受け付けられませんでした。\n"
                m += result
                await client.send_message(message.author, m)
            else:
                m = args[1] + "への投票を受け付けました。\n開票までなら変更することもできるよ。"
                await client.send_message(message.author, m)

        # 全員投票したら告知
        if w.unvoters == []:
            force_break = True
            m = "全員の投票を確認しました。\n5秒後に開票します。"
            play_sound("yattaze.mp3")
            await client.send_message(game_channel, m)
            loop.call_later(5, execute, game_channel)
            # loop.call_later(2, wordwolf, end_time, loop, message.channel, [])

    if args[0] in ["wolf", "wolfs", "wolf_size"]:
        if w.state != "accepting_player":
            m = "そのコマンドは参加者受付中にしか実行できないよ。"
            await client.send_message(message.channel, m)
            return
        if argsize < 2:
            m = "狼の数を変えるには !wolf [狼の数] だよ。"
            await client.send_message(message.channel, m)
        else:
            try:
                result = w.set_wolf_size(int(args[1]))
                m = "狼の数を" + str(result) + "人にしました。"
            except Exception:
                m = "ｱﾜﾜﾜ...(整数を入力してください)"
            await client.send_message(message.channel, m)

    if args[0] in ["debug"]:
        m = w.get_info()
        await client.send_message(message.author, m)

    if args[0] in ["execute"]:
        if w.state != "theme_discussion":
            m = "そのコマンドはゲーム中にしか実行できないよ。"
            await client.send_message(message.channel, m)
            return
        execute(message.channel, False)

    if args[0] in ["execute!"]:
        if w.state != "theme_discussion":
            m = "そのコマンドはゲーム中にしか実行できないよ。"
            await client.send_message(message.channel, m)
            return
        execute(message.channel, True)

    if args[0] in ["comeback"]:
        comeback("wolf_comeback")
        m = "直前のゲームの結果を「少数派逆転勝利」に書き換えました。"
        await client.send_message(message.channel, m)

    if args[0] in ["seed"]:
        if w.state != "accepting_player":
            m = "そのコマンドは参加者受付中にしか実行できないよ。"
            await client.send_message(message.channel, m)
            return
        if argsize < 2:
            m = "シード値の指定は !seed [呪文] だよ。"
            await client.send_message(message.channel, m)
        try:
            w.set_seed(int(args[1]))
            m = "シード値を " + args[1] + " に設定しました。"
            await client.send_message(message.channel, m)
        except Exception:
            w.set_seed(args[1])
            m = "シード値を " + args[1] + " に設定しました。"
            await client.send_message(message.channel, m)

    if args[0] in ["category", "cat"]:
        if w.state != "accepting_player":
            m = "そのコマンドは参加者受付中にしか実行できないよ。"
            await client.send_message(message.channel, m)
            return
        # カテゴリー選択

        if argsize < 2:
            w.set_categories(None)
            m = "出題カテゴリを初期化しました。\nカテゴリの指定は !category [カテゴリ名] だよ。"
            await client.send_message(message.channel, m)
        else:
            m = "出題カテゴリを"
            for i in args[1:]:
                m += i
                m += ","
            m = m[:-1]
            m += "に設定しました。初期化する場合は!catだよ。"
            await client.send_message(message.channel, m)
            w.set_categories(args[1:])

    if args[0] in ["wordwolf", "ww"]:
        if w.state != "accepting_player":
            m = "そのコマンドは参加者受付中にしか実行できないよ。"
            await client.send_message(message.channel, m)
            return
        game_channel = message.channel

        if len(w.players) == 0:
            m = "参加者0人"
            await client.send_message(message.channel, m)
            return

        if len(w.players) < w.wolf_size:
            m = "指定された狼人数(" + str(w.wolf_size) + ")が参加者数(" + \
                str(len(w.players)) + ")を超えています。\n"
            await client.send_message(message.channel, m)
            return

        if client.user != message.author:
            given_time = 1
            if(argsize > 1):
                given_time = float(args[1])
            given_time *= 60
            m = "ワードウルフを始めます。\n議論の制限時間は" + \
                str(int(given_time / 60)) + "分です。\nDMから自分のテーマを確認してね。"
            if w.categories != []:
                m += "\nカテゴリ: "
                for i in w.categories:
                    m += i
                    m += ","
                m = m[:-1]

            await client.send_message(message.channel, m)

            w.start()

            # テーマを伝える
            for i in w.players:
                info = w.get_info()
                print(info)
                if info["players"][i]["role"] == "wolf":
                    m = "あなたは「" + info["game"]["theme"][1] + "」"
                else:
                    m = "あなたは「" + info["game"]["theme"][0] + "」"
                await client.send_message(dm_address[i], m)

            m = "参加者: " + str(len(w.players)) + "人\n"
            for i in w.players:
                m += i
                m += "\n"
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

    if args[0] in ["nickname"]:
        if argsize < 3:
            m = "ニックネームの追加は !nickname [真名] [ニックネーム] だよ。"
            await client.send_message(message.channel, m)
        else:
            add_nickname(args[1], args[2])
            m = "ニックネームを追加しました。"
            await client.send_message(message.channel, m)

    if args[0] in ["shownick"]:
        if argsize < 2:
            m = "ニックネームの確認は !shownick [ニックネーム] だよ。"
            await client.send_message(message.channel, m)
        if args[1] == nickname(args[1]):
            m = "そのニックネームは登録されてないよ。"
            await client.send_message(message.channel, m)
            return
        m = "ニックネーム変換: " + args[1] + "\t->\t" + nickname(args[1])
        await client.send_message(message.channel, m)

    if args[0] in ["stop"]:
        force_break = True
        print(given_time, ql_time)
        m = "狼を当ててください。\n議論の制限時間は" + str(given_time - ql_time) + "秒です。"
        end_time = loop.time() + given_time - ql_time
        loop.call_later(2, wordwolf, end_time, loop, message.channel, [])
        await client.send_message(message.channel, m)

    if args[0] in ["kill"]:
        force_break = True
        print(force_break)
        m = "実行中のゲームを終了します..."
        await client.send_message(message.channel, m)
        print(force_break)
        m = "完了"
        await client.send_message(message.channel, m)

    if args[0] in ["debugkill"]:
        m = "プロセスを終了します。"
        await client.send_message(message.channel, m)
        quit()

    if args[0] in ["finish", "fa"]:
        finish(message.channel)

    if args[0] in ["outputlog"]:
        import json
        import pickle
        try:
            with open('pickles/game_result.pickle', mode='rb') as f:
                history = pickle.load(f)
            with open("history.json", "w") as f:
                json.dump(history, f)

            # JSONファイルを送る
            with open("history.json", "r") as f:
                await client.send_file(message.channel, f)
        except Exception:
            print("ERROR!")
            m = "ｱﾜﾜﾜ...（json出力失敗）"
            await client.send_message(message.channel, m)
            return
        m = "ゲームログをjson形式で書き出しました。"
        await client.send_message(message.channel, m)


import time


async def send(channel, message):
    # print("called")
    await client.send_message(channel, message)
    # print("sent")


async def playing(txt):
    await client.change_presence(game=discord.Game(name=txt))


def nickname(nick):
    import pickle
    """
    ニックネームから正しいユーザー名を得る
    """
    nickname = {}
    with open("pickles/nickname.pickle", mode="rb") as f:
        nickname = pickle.load(f)
    try:
        return nickname[nick]
    except:
        return nick


def add_nickname(true, nick):
    import pickle
    """
    ニックネーム辞書に追加する
    """
    nickname = {}
    with open("pickles/nickname.pickle", mode="rb") as f:
        nickname = pickle.load(f)
    nickname[nick] = true
    with open("pickles/nickname.pickle", mode="wb") as f:
        pickle.dump(nickname, f)
    return


def finish(channel):
    info = w.get_info()
    if info == {}:
        m = "ゲーム記録が存在しません...ｱﾜﾜﾜ"
        asyncio.ensure_future(send(channel, m))
        return

    # print(info["game"]["theme"])
    theme = "多数派は「" + info["game"]["theme"][0] + \
        "」\n少数派は「" + info["game"]["theme"][1] + "」\n"
    wolfs = "狼は"
    for i in w.players:
        if info["players"][i]["role"] == "wolf":
            wolfs += i
            wolfs += " "

    m = "\nでした。ゲームを終了します。"
    asyncio.ensure_future(send(channel, theme + wolfs + m))


def get_vote_info():
    """
    infoから投票情報の文字列を作成
    """
    max_len = 0
    for i in w.get_info()["game"]["valid_voters"]:
        max_len = max(max_len, len(i))

    m = "=======VOTE INFO=======\n"
    for i in w.get_info()["game"]["valid_voters"]:
        target = w.get_info()["players"][i]["vote"]
        m += i + "\t->\t" + target + "\n"

    m += "=======================\n"
    return m


def dump_log(winner):
    """
    winner陣営勝利でinfoを書き込む
    """
    import pickle
    info = w.get_info()
    info["winner"] = winner

    try:
        with open('pickles/game_result.pickle', mode='rb') as f:
            history = pickle.load(f)
    except Exception:
        history = []
    history.append(info)
    with open('pickles/game_result.pickle', mode='wb') as f:
        pickle.dump(history, f)

    print(history)


def comeback(winner):
    import pickle
    """
    最後に記録されたゲームの勝者をwinnerに書き換える
    """
    try:
        with open('pickles/game_result.pickle', mode='rb') as f:
            history = pickle.load(f)
    except Exception:
        print("FAILED: no pickle found")
        return
    history[-1]["winner"] = winner
    with open('pickles/game_result.pickle', mode='wb') as f:
        pickle.dump(history, f)

    print(history)


def execute(channel, force=False):
    global force_break
    force_break = True
    m = get_vote_info()
    result, executed, role = w.execute(force)
    if result.startswith("Finish") or force:
        execute = "処刑"
        if force == True:
            print("forced execute!")
            m += "処刑が強行されました。"

        m += "投票の結果、" + executed + " さんが" + execute + "されました。\n"
        if role == "villager":
            m += executed + " さんは多数派でした。よって、勝者は少数派である\n"
            for i in w.wolfs:
                m += i
                m += " さん\n"
            m += "に確定しました。"
            asyncio.ensure_future(send(channel, m))
            finish(channel)
            dump_log("wolf")
            # m+="ゲームを終了します。"
        else:
            m += executed + " さんは少数派でした。\nテーマは「" + \
                w.info["game"]["theme"][1] + \
                "」です。\n多数派のお題を言い当てれば逆転勝利だよ。\n逆転勝利したら !comeback してね（ゲーム履歴を修正するため）"
            asyncio.ensure_future(send(channel, m))
            dump_log("villager")
            # m+="ゲームを終了します。"
    elif result.startswith("Tie"):
        m += "投票の結果、処刑対象を一人に絞れませんでした。\n最多得票者は\n"
        for i in executed:
            m += i
            m += " さん\n"
        m += "です。2分間の再議論の後、\nもう一度投票してください。"
        asyncio.ensure_future(send(channel, m))
        end_time = loop.time() + 120
        loop.call_later(2, wordwolf, end_time, loop, channel)
    else:
        force_break = False
        m = "未投票の人がいます。"
        asyncio.ensure_future(send(channel, m))


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
                    if (left_time < 70):
                        play_sound("1minute.mp3")
                    m = "残り" + str(int(left_time / 60)) + "分です。"
                elif left_time >= 5:
                    if left_time > 25 and left_time < 35:
                        play_sound("30sec.mp3")
                    m = "残り" + str(int(left_time)) + "秒です。"
                else:
                    # m = str(int(left_time))
                    play_sound("timeup.mp3")
                    m = "制限時間を過ぎました。\n"
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
        m = "投票に移ってください。"
        asyncio.ensure_future(playing(""))
        asyncio.ensure_future(send(message_channel, m))
        loop.call_soon(loop.stop)  # 単に loop.stop() でもいい


def play_sound(what):
    """
    whatで指定された音を再生する
    """
    global voice
    if voice == None:
        print("voice is offline.")
        return
    try:
        player = voice.create_ffmpeg_player("sound/"+what)
        player.start()
        return
    except Exception:
        print("No sound found:", what)


def wordwolf(end_time, loop, message_channel, precaution_time=None):
    left_time = end_time - loop.time()
    print(datetime.datetime.now(), left_time, "remaining")

    global force_break
    global bgm
    if force_break == True:
        asyncio.ensure_future(playing(""))
        print("wordwolf: killed")
        return

    # 初回起動時
    if precaution_time == None:
        if bgm != None:
            bgm.stop()
            bgm = None
            m = "動画音声の再生を停止しました（複数の音声を一度に流すとクラッシュするため）"
            asyncio.ensure_future(send(message_channel, m))
        play_sound("game_start.wav")
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
                    if (left_time < 70):
                        play_sound("1minute.mp3")
                    m = "残り" + str(int(left_time / 60)) + "分です。"
                elif left_time >= 10:
                    if left_time > 25 and left_time < 35:
                        play_sound("30sec.mp3")
                    if left_time > 5 and left_time < 15:
                        play_sound("10sec.mp3")
                    m = "残り" + str(int(left_time)) + "秒です。"
                else:
                    # m = str(int(left_time))
                    m = "制限時間を過ぎました。"
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
        play_sound("timeup.mp3")
        asyncio.ensure_future(playing(""))
        m = "投票に移ってください。"
        asyncio.ensure_future(send(message_channel, m))
        # loop.call_soon(loop.stop)  # 単に loop.stop() でもいい


loop = asyncio.get_event_loop()

# Schedule the first call to wordwolf()
# end_time = loop.time() + 5.0
# loop.call_soon(wordwolf, end_time, loop)

# Blocking call interrupted by loop.stop()
# loop.run_forever()
# loop.close()

# token にDiscordのデベロッパサイトで取得したトークンを入れてください
token = ""
with open("token.txt") as f:
    token = f.read()
client.run(token)
