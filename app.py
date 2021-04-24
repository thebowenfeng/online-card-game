import os
from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from random import shuffle, randint

app = Flask(__name__)
sio = SocketIO(app, cors_allowed_origins="*")
DATABASE_URI = os.environ.get('DATABASE_URL')

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
db = SQLAlchemy(app)

def logging(func):
    wraps(func)
    def wrapper(*args):
        print(f"Function {func.__name__} is called. Argument: {args[0]}")
        return func(*args)
    return wrapper

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sid = db.Column(db.String(100), nullable=False)
    deck = db.Column(db.String(500), nullable=True)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"))
    player_id = db.Column(db.Integer, nullable=True)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_num = db.Column(db.Integer, nullable=False)
    in_game = db.Column(db.Boolean, nullable=False)
    players = db.relationship("Player", backref="room")
    landlord_id = db.Column(db.Integer, nullable=True)
    current_player = db.Column(db.Integer, nullable=True)
    pass_num = db.Column(db.Integer, nullable=False)
    prev_play = db.Column(db.String(100), nullable=True)

@sio.on("join_room")
@logging
def join_a_room(data):
    sid = data["sid"]
    name = data["name"]
    player_obj = Player(name=name, sid=sid)
    db.session.add(player_obj)
    room_list = Room.query.all()
    is_added = False

    for room in room_list:
        if room.in_game == False and room.player_num < 3:
            player_obj.room = room
            room.player_num += 1
            player_obj.player_id = room.player_num
            db.session.commit()
            join_room(room.id)

            sio.emit("wait_gamestart", {"id": room.player_num, "sid": sid}, room=room.id)

            if room.player_num == 3:
                room.in_game = True
                db.session.commit()
                index_deck = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2", "sJoker", "bJoker"]

                full_deck = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2", "sJoker", "bJoker", "3",
                             "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2", "3", "4", "5", "6", "7", "8",
                             "9", "10", "J", "Q", "K", "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K",
                             "A", "2"]

                shuffle(full_deck)
                wild_cards = full_deck[:3]

                p1_deck = sorted(full_deck[3:20], key=lambda x: index_deck.index(x))
                p2_deck = sorted(full_deck[20:37], key=lambda x: index_deck.index(x))
                p3_deck = sorted(full_deck[37:54], key=lambda x: index_deck.index(x))

                landlord_id = randint(1, 3)

                sio.emit("start_game", {1: p1_deck, 2: p2_deck, 3:p3_deck, "wild_cards": wild_cards, "landlord":landlord_id}, room=room.id)

            is_added = True
            break

    if is_added:
        pass
    else:
        new_room = Room(in_game=False, player_num=1, pass_num=0)
        db.session.add(new_room)
        player_obj.room = new_room
        player_obj.player_id = 1
        db.session.commit()
        join_room(new_room.id)
        sio.emit("wait_gamestart", {"id": new_room.player_num, "sid":sid}, room=new_room.id)


@sio.on("deck_receive")
@logging
def receive(data):
    sid = data["sid"]
    player_obj = Player.query.filter_by(sid=sid).first()
    room_obj = player_obj.room


    player_list = room_obj.players
    p1_obj = player_list[0]
    p2_obj = player_list[1]
    p3_obj = player_list[2]

    player_infos = [(p1_obj.player_id, p1_obj.deck), (p2_obj.player_id, p2_obj.deck), (p3_obj.player_id, p3_obj.deck)]

    player_obj.deck = " ".join(data["deck"])
    room_obj.landlord_id = data["landlord_id"]
    room_obj.current_player = room_obj.landlord_id
    db.session.commit()

    if player_obj.player_id == room_obj.landlord_id:
        sio.emit("play", {"init":True, "player_id": player_obj.player_id, "is_turn":True, "info":player_infos}, room=room_obj.id)
    else:
        sio.emit("play", {"init":True, "player_id": player_obj.player_id, "is_turn":False, "info":player_infos}, room=room_obj.id)


@sio.on("receive_play")
@logging
def receive_play(data):
    player_id = data["player_id"]
    sid = data["sid"]
    deck = data["deck"]
    prev_play = data["prev"]

    player_obj = Player.query.filter_by(sid=sid).first()
    player_obj.deck = " ".join(deck)

    room_obj = player_obj.room
    room_obj.current_player = (room_obj.current_player % 3) + 1
    db.session.commit()

    if len(deck) == 0:
        sio.emit("win", {"id":player_id, "room_id":room_obj.id, "name":player_obj.name}, room=room_obj.id)
    else:
        player_list = room_obj.players
        p1_obj = player_list[0]
        p2_obj = player_list[1]
        p3_obj = player_list[2]

        player_infos = [(p1_obj.player_id, p1_obj.deck), (p2_obj.player_id, p2_obj.deck), (p3_obj.player_id, p3_obj.deck)]

        if prev_play == "pass":
            room_obj.pass_num += 1
            if room_obj.pass_num == 2:
                room_obj.pass_num = 0
                room_obj.prev_play = None
                sio.emit("play", {"round_finish":True, "player_id": room_obj.current_player, "info": player_infos},
                         room=room_obj.id)
            else:
                sio.emit("play", {"player_id": room_obj.current_player, "info": player_infos, "prev_play": prev_play, "ptb": room_obj.prev_play},
                         room=room_obj.id)
        else:
            room_obj.pass_num = 0
            room_obj.prev_play = prev_play
            sio.emit("play", {"player_id": room_obj.current_player, "info":player_infos, "prev_play":room_obj.prev_play}, room=room_obj.id)

        db.session.commit()

@sio.on("reset")
@logging
def reset(data):
    player_obj = Player.query.filter_by(sid=data["sid"]).first()
    db.session.delete(player_obj)
    db.session.commit()

    room_obj = Room.query.filter_by(id=data["room_id"]).first()
    if room_obj is not None:
        db.session.delete(room_obj)
        db.session.commit()

    leave_room(data["room_id"])
    sio.emit("queue", {})


if __name__ == '__main__':
    app.run(debug=True)

