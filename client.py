import socketio
from card import Card
import time

sio = socketio.Client()
PLAYER_ID = None
DECK = []
INDEX_DECK = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2", "sJoker", "bJoker"]

@sio.event()
def connect():
    print("Connection established")

@sio.on("wait_gamestart")
def wait(data):
    global PLAYER_ID
    if data["sid"] == sio.sid:
        PLAYER_ID = data["id"]
    print("Player joined a room! Player ID is: " + str(data["id"]))
    print("Your player ID is: " + str(PLAYER_ID))

@sio.on("start_game")
def start(data):
    global PLAYER_ID
    global DECK
    global INDEX_DECK

    print("Game has started")
    DECK = data[str(PLAYER_ID)]

    if PLAYER_ID == data["landlord"]:
        print("You are the landlord!")
        DECK = sorted(DECK + data["wild_cards"], key=lambda x: INDEX_DECK.index(x))

    print(f"Your deck is: {str(DECK)}")
    sio.emit("deck_receive", {"player_id": PLAYER_ID, "sid": sio.sid, "landlord_id":data["landlord"], "deck":DECK})

def isValid(play):
    global INDEX_DECK

    play_list = play.split(" ")
    #print(play_list)

    for card in play_list:
        if card not in INDEX_DECK:
            return False

    if len(play_list) == 2:
        if play_list[0] != play_list[1]:
            return False
    elif len(play_list) == 3:
        if play_list[0] == play_list[1] == play_list[2]:
            return True
        else:
            return

    return True

@sio.on("play")
def play(data):
    global PLAYER_ID
    global DECK
    player_id = data["player_id"]

    if "init" in data:
        if player_id == PLAYER_ID and data["is_turn"]:
            for pid, pdeck in data["info"]:
                if pdeck != None:
                    print(f"Player {pid} currently has {len(pdeck.split())} cards in their deck")

            while True:
                time.sleep(0.2)
                in_deck = True
                play = input("Enter your play: ")

                if not isValid(play):
                    print("Your play is not valid")
                    continue

                temp = DECK.copy()
                for card in play.split(" "):
                    if card not in temp:
                        in_deck = False
                        print("Your card is not in your deck")
                        break
                    temp.remove(card)

                if not in_deck:
                    continue

                break

            for card in play.split(" "):
                DECK.remove(card)

            sio.emit("receive_play", {"player_id":PLAYER_ID, "sid":sio.sid, "deck":DECK, "prev":play})

        elif player_id == PLAYER_ID and not data["is_turn"]:
            for pid, pdeck in data["info"]:
                if pdeck != None:
                    print(f"Player {pid} currently has {len(pdeck.split())} cards in their deck")

            print("It is not your turn, waiting on the current player to make a play...")

    elif "round_finish" in data:
        if player_id == PLAYER_ID:
            for pid, pdeck in data["info"]:
                if pdeck != None:
                    print(f"Player {pid} currently has {len(pdeck.split())} cards in their deck")

            print(DECK)
            while True:
                time.sleep(0.2)
                in_deck = True
                play = input("Enter your play: ")

                if not isValid(play):
                    print("Your play is not valid")
                    continue

                temp = DECK.copy()
                for card in play.split(" "):
                    if card not in temp:
                        in_deck = False
                        print("Your card is not in your deck")
                        break
                    temp.remove(card)

                if not in_deck:
                    continue


                break

            for card in play.split(" "):
                DECK.remove(card)

            sio.emit("receive_play", {"player_id":PLAYER_ID, "sid":sio.sid, "deck":DECK, "prev":play})

        else:
            print(f"Round finished! Player {player_id} is starting a new round. Waiting on play...")
    else:
        if player_id == PLAYER_ID:
            for pid, pdeck in data["info"]:
                if pdeck != None:
                    print(f"Player {pid} currently has {len(pdeck.split())} cards in their deck")

            if "ptb" in data:
                if player_id == 1:
                    print(f"Player 3 has played: {data['prev_play']}. The play to beat is: {data['ptb']}. Waiting on the next player...")
                else:
                    print(f"Player {player_id - 1} has played: {data['prev_play']}. The play to beat is {data['ptb']}. Waiting on the next player...")
            else:
                if player_id == 1:
                    print(f"Player 3 has played: {data['prev_play']}. Waiting on the next player...")
                else:
                    print(f"Player {player_id - 1} has played: {data['prev_play']}. Waiting on the next player...")


            while(True):
                time.sleep(0.2)
                print(DECK)
                in_deck = True
                play = input("Enter your play: ")

                if play == "pass":
                    sio.emit("receive_play", {"player_id": PLAYER_ID, "sid": sio.sid, "deck": DECK, "prev": play})
                    break
                else:
                    if not isValid(play):
                        print("Your play is not valid")
                        continue

                    temp = DECK.copy()
                    for card in play.split(" "):
                        if card not in temp:
                            in_deck = False
                            print("Your card is not in your deck")
                            break
                        temp.remove(card)

                    if not in_deck:
                        continue

                    if "ptb" in data:
                        if len(play.split()) != len(data["ptb"].split()):
                            print("The play is not of the same type.")
                            continue

                        if Card(play) > Card(data["ptb"]):
                            for card in play.split(" "):
                                DECK.remove(card)

                            sio.emit("receive_play", {"player_id": PLAYER_ID, "sid": sio.sid, "deck": DECK, "prev": play})
                            time.sleep(0.3)
                            break
                        else:
                            print("The current play does not beat the previous play")
                    else:
                        if len(play.split()) != len(data["prev_play"].split()):
                            print("The play is not of the same type.")
                            continue

                        if Card(play) > Card(data["prev_play"]):
                            for card in play.split(" "):
                                DECK.remove(card)

                            sio.emit("receive_play", {"player_id": PLAYER_ID, "sid": sio.sid, "deck": DECK, "prev": play})
                            time.sleep(0.3)
                            break
                        else:
                            print("The current play does not beat the previous play")

        else:
            for pid, pdeck in data["info"]:
                if pdeck != None:
                    print(f"Player {pid} currently has {len(pdeck.split())} cards in their deck")

            if player_id == 1:
                print(f"Player 3 has played: {data['prev_play']}. Waiting on the next player...")
            else:
                print(f"Player {player_id - 1} has played: {data['prev_play']}. Waiting on the next player...")


@sio.on("win")
def win(data):
    global PLAYER_ID
    if data["id"] == PLAYER_ID:
        print("You won! Congratulations!")
    else:
        print(f"You lost. {data['name']} has won the game!")

    sio.emit("reset", {"sid":sio.sid, "room_id":data["room_id"]})


@sio.on("queue")
def queue(data):
    name = input("Enter your name: ")
    sio.emit("join_room", {"sid": sio.sid, "name": name})

if __name__ == "__main__":
    name = input("Enter your name: ")
    sio.connect("https://bowenfeng.pythonanywhere.com/")
    sio.emit("join_room", {"sid": sio.sid, "name": name})