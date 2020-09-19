import datetime
import time
import asyncio
import json
import random

from copy import deepcopy
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from .views import all_user_objects, get_user_cards, usernames
from .declare_winner import declare_winer

# from .models import Thread, ChatMessage
gameroom = {
    "players_list": list,
    "game_status": {
        "total_money": int,
        "running": bool,
        "min_bid": int,
        "turn": str
    }
}
all_gamerooms = []


class ChatConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("Connected", event)
        await self.send({
            "type": "websocket.accept"
        })
        try:
            all_user_objects[-1]["thread"] = self
        except:
            await asyncio.sleep(1)
            all_user_objects[-1]["thread"] = self

        if len(all_user_objects) == 2:
            loc_gameroom = deepcopy(gameroom)
            loc_gameroom["players_list"] = all_user_objects.copy()
            all_gamerooms.append(loc_gameroom)
            all_user_objects[:2] = []
            await start_game(loc_gameroom)
        else:
            await waiting_4_friend(self)

    async def websocket_receive(self, event):
        for gameroom in all_gamerooms:
            if gameroom["game_status"]["running"]:
                for player in gameroom["players_list"]:
                    if self == player["thread"]:
                        message = json.loads(event["text"])
                        if message["class_"] == "chat":
                            message["class_"] = "players-chat"
                            message["sender"] = player["name"]
                            message = json.dumps(message)
                            await chitChat(gameroom["players_list"], message, self)
                        elif message["class_"] == "pack":
                            if gameroom["game_status"]["turn"] == player["name"]:
                                message["sender"] = player["name"]
                            await pack_game(gameroom, message)
                        elif message["class_"] == "place":
                            if gameroom["game_status"]["turn"] == player["name"]:
                                message["sender"] = player["thread"]
                                await place_bid(gameroom, message)
                        elif message["class_"] == "show":
                            print("msggot")
                            if gameroom["game_status"]["turn"] == player["name"]:
                                message["sender"] = player["name"]
                                await show_cards(gameroom, message)

    async def websocket_disconnect(self, event):
        print("Disconnected", event)
        await self.send({
            "type": "websocket.close"
        })
        userRemoved = False
        for user in all_user_objects:
            if user["thread"] == self:
                all_user_objects.remove(user)
                usernames.remove(user["name"])
                userRemoved = True
        if not userRemoved:
            for local_gameroom in all_gamerooms:
                for player in local_gameroom["players_list"]:
                    if self == player["thread"]:
                        local_gameroom["players_list"].remove(player)
                        local_gameroom["game_status"] = gameroom["game_status"]
                        usernames.remove(player["name"])
                    else:
                        player["money"] = 1000
                online_player = local_gameroom["players_list"][0]
                await opp_disconnect(online_player["thread"])
                await waiting_4_friend(online_player["thread"])
                all_user_objects.append(online_player)

        for _ in range(all_gamerooms.count([])):
            all_gamerooms.remove([])


async def show_cards(loc_gameroom, message):
    card_owner = {}
    for player in loc_gameroom["players_list"]:
        card_owner.update({
            " ".join(player["cards"]): player["thread"]
        })
    winner = declare_winer(card_owner)
    data_to_send = {
        "class_": "show_cards",
        "sender": message["sender"]
    }
    for player in loc_gameroom["players_list"]:
        data_to_send["opp_cards"] = loc_gameroom["players_list"][1 -
                                                                 loc_gameroom["players_list"].index(player)]["cards"]
        await player["thread"].send({
            "type": "websocket.send",
            "text": json.dumps(data_to_send),

        })
    await post_game(loc_gameroom, winner)


async def start_game(loc_gameroom, re=False):
    turn = random.choice(loc_gameroom["players_list"])["name"]
    loc_gameroom["game_status"]["running"] = True
    loc_gameroom["game_status"]["min_bid"] = 10
    loc_gameroom["game_status"]["turn"] = turn
    for player in loc_gameroom["players_list"]:
        player["money"] -= 10
    loc_gameroom["game_status"]["total_money"] = 10 * \
        len(loc_gameroom["players_list"])

    for players in loc_gameroom["players_list"]:
        players["cards"] = get_user_cards()

        new_player, thread = exclude_key(players, "thread")

        opp_info = loc_gameroom["players_list"][1 -
                                                loc_gameroom["players_list"].index(players)]
        new_opp, _ = exclude_key(opp_info, "thread")
        new_opp["cards"] = ["hidden", "hidden", "hidden"]

        new_player.update(
            {"opp_info": new_opp, "class_": 'startgame', "game_stats": loc_gameroom["game_status"], "re": re})

        await thread.send({
            "type": "websocket.send",
            "text": json.dumps(new_player)
        })
        print("match msg sent \n")


async def opp_disconnect(thread):
    await thread.send({
        "type": "websocket.send",
        "text": json.dumps({"class_": "opp_disconnect"})
    })
    print("disconnected msg sent \n")


async def waiting_4_friend(thread):
    await thread.send({
        "type": "websocket.send",
        "text": json.dumps({"class_": "waiting", "message": "waiting for a match"})
    })
    print("waiting msg sent \n")


async def chitChat(players_list, message, sender):
    for player in players_list:
        if player["thread"] != sender:
            await player["thread"].send({
                "type": "websocket.send",
                "text": message
            })


async def pack_game(loc_gameroom, message):
    winner = None
    for player in loc_gameroom["players_list"]:
        opp = loc_gameroom["players_list"][1 -
                                           loc_gameroom["players_list"].index(player)]
        if opp["name"] != message["sender"]:
            winner = opp["thread"]
        data_to_send = {
            "class_": "pack",
            "sender": message["sender"],
            "opp_cards": opp['cards']
        }
        await player["thread"].send({
            "type": "websocket.send",
            "text": json.dumps(data_to_send)
        })

    await post_game(loc_gameroom, winner)


async def place_bid(gameroom, message):
    bid_amount = message["bid_amount"]
    bid_increment = bid_amount - gameroom["game_status"]["min_bid"]
    if (30 < bid_increment < 0) or (bid_increment < 0):
        await js_changed(message["sender"])
    else:
        if bid_increment > 0:
            gameroom["game_status"]["min_bid"] = bid_amount
        for player in gameroom["players_list"]:
            if player["thread"] == message["sender"]:
                if player["money"] > bid_amount:
                    player["money"] -= bid_amount
                else:
                    await js_changed(player["thread"])
                opp = gameroom["players_list"][1 -
                                               gameroom["players_list"].index(player)]

        gameroom["game_status"]["total_money"] += bid_amount
        gameroom["game_status"]["turn"] = switch_turn(gameroom)

        for player in gameroom["players_list"]:
            opp_money = gameroom["players_list"][1 -
                                                 gameroom["players_list"].index(player)]["money"]

            data_to_send = {
                "class_": "place_bid",
                "opp_money": opp_money,
                "money": player["money"],
                "game_stats": gameroom["game_status"]
            }
            await player["thread"].send({
                "type": "websocket.send",
                "text": json.dumps(data_to_send)
            })

        if opp["money"] < bid_amount:
            data_to_send = {
                "class_": "insufficient_money",
                "poor": opp["name"]
            }
            for player in gameroom["players_list"]:
                await player["thread"].send({
                    "type": "websocket.send",
                    "text": json.dumps(data_to_send)
                })
            await end_game(gameroom, message["sender"])


def switch_turn(gameroom):
    curr = gameroom["game_status"]["turn"]
    for player in gameroom["players_list"]:
        if player["name"] != curr:
            return player["name"]


async def end_game(loc_gameroom, winner):
    winner_name = None
    for player in loc_gameroom["players_list"]:
        if player["thread"] == winner:
            winner_name = player["name"]
    data_to_send = {
        "class_": "end_game",
        "winner": winner_name
    }
    loc_gameroom["game_Status"] = gameroom["game_status"]
    for player in loc_gameroom["players_list"]:
        player["money"] = 1000
        await player["thread"].send({
            "type": "websocket.send",
            "text": json.dumps(data_to_send)
        })


async def js_changed(criminal):
    data_to_send = {
        "class_": "js_changed",
    }
    await criminal.send({
        "type": "websocket.send",
        "text": json.dumps(data_to_send)
    })


async def post_game(loc_gameroom, winner):
    winner_dict: dict
    loc_gameroom["game_status"]["running"] = False
    loc_gameroom["game_status"]["turn"] = None
    loc_gameroom["game_status"]["min_bid"] = 10

    for player in loc_gameroom["players_list"]:
        if player["thread"] == winner:
            winner_dict = player
            player["money"] += loc_gameroom["game_status"]["total_money"]
            opp = loc_gameroom["players_list"][1 -
                                               loc_gameroom["players_list"].index(player)]
    if opp["money"] <= loc_gameroom["game_status"]["min_bid"]:
        data_to_send = {
            "class_": "insufficient_money",
            "poor": opp["name"]
        }
        for player in loc_gameroom["players_list"]:
            await player["thread"].send({
                "type": "websocket.send",
                "text": json.dumps(data_to_send)
            })
        await end_game(loc_gameroom, winner_dict["thread"])
    else:
        loc_gameroom["game_status"]["total_money"] = 0
        data_to_send = {
            "class_": "post_game",
            "winner": winner_dict["name"],
        }

        for player in loc_gameroom["players_list"]:
            await player["thread"].send({
                "type": "websocket.send",
                "text": json.dumps(data_to_send)
            })

        await asyncio.sleep(10)
        await start_game(loc_gameroom, re=True)


def exclude_key(dictionary, key):
    new_dict = dictionary.copy()
    removed = new_dict.pop(key)
    return new_dict, removed
