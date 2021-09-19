from logging import NullHandler
from flask import Flask, render_template, send_from_directory, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from werkzeug import datastructures
from random import random
from threading import Event
import random

wordlist = ['Bunny', 'Cow', 'Sky', 'Painting','Minecraft', 'Smartphone', 'IKEA', 'Dog', 'Cat', 'Ham Sandwich', 'Water Bottle', 'Plant', 'Earth', 'Mars', 'Saturn','Car','Computer','Boat','Maldives','Airport', 'Pen', 'Pencil', 'Wardrobe', 'Canada', 'Fish', 'Bank', 'Door', 'Fox','Chimpanzee','Monkey','Sunflower']


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

games = [
    {'users':{'bob':{'score':10,'drawing':False},'james':{'score':10,'drawing':False}},'gamenumber':23, 'gamehostusername':'bob', 'closed':False, 'word':''}
]

def choosewords():
    while True:
        words = random.choices(wordlist, k=3)
        print(words)
        if len(set(words)) != len(words):
            continue
        else:
            break
    return words

#This function needs to be rewritten once I have gathered enough energy
def generateandchecknumber():
  while True:
    number = int(1000000*random.random())

    taken = False

    for game in games:
      if game['gamenumber'] == number:
        taken = True
        break;
      else:
        continue;
    
    if (taken):
      continue;
    else:
      return number

def checkgameexists(gamenumber):
    for game in games:
        if (game['gamenumber']==gamenumber):
            return True
        else:
            continue
    return False

def gamelocked(gamenumber):
    for game in games:
        if (game['gamenumber']==gamenumber):
            if (game['closed']):
                return True;
        else:
            continue
    return False

def usernametaken(gamenumber,username):
    for game in games:
        if (game['gamenumber']==gamenumber):
            if username in game['users']:
                return True
            else:
                return False
        else:
            continue

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/game", methods=["POST"])
def game():
    if checkgameexists(int(request.form['gamenumber'])):
        if not(usernametaken(int(request.form['gamenumber']),request.form['username'])):
            if not gamelocked(int(request.form['gamenumber'])):
                return render_template('game.html', data=request.form.to_dict())
            else:
                return render_template('error.html', message="Game has been locked")
        else:
            return render_template('error.html', message="The username '"+request.form['username']+"' is taken or is from a user who has disconnected")
    else:
        return render_template('error.html', message="This game doesn't exist yet")

@app.route("/createpage", methods=["POST"])
def createpage():
        return render_template('createpage.html', data=request.form.to_dict())

@app.route("/gamehost", methods=["POST"])
def gamehost():
        data=request.form.to_dict()
        gamecode = generateandchecknumber()
        games.append({'users':{},'gamenumber':gamecode, 'gamehostusername':data['hostusername'], 'closed':False, 'drawduration':int(data['drawduration']),'word':''})
        return render_template('game.html', data={"gamenumber":str(gamecode),"username":data['hostusername']})

@app.route('/static/<path:path>')
def sendfiles(path):
    return send_from_directory('static', path)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['gamenumber']

    
    for game in games:
        if int(room)==game['gamenumber']:
            game['users'][username]={'score':0,'drawing':False}
            break;
        else:
            continue;        

    join_room(room)
    emit("message",{'text':username + ' has entered','username':'Server', 'gamenumber':data['gamenumber']}, to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['gamenumber']

    for game in games:
        if int(room)==game['gamenumber']:
            game['users'].pop(username)
            break;
        else:
            continue;

    for game in games:
        if int(room)==(game['gamenumber']) and username==game['gamehostusername']:
            emit("message",{'text':'The game has been shut since the host user left', 'gamenumber':data['gamenumber']}, to=room)          
            games.remove(game)
            break;
        else:
            continue;

    leave_room(room)
    emit("message",{'text':username + ' has left','username':'Server', 'gamenumber':data['gamenumber']}, to=room)

@socketio.on('startgame')
def startgame(data):
    username = data['username']
    room = data['gamenumber']

    for game in games:
        if int(room)==(game['gamenumber']):
            if username==game['gamehostusername']:
                emit("message",{'text':'The game has been locked','username':'Server', 'gamenumber':data['gamenumber']}, to=room) 
                game['closed']=True
            break;
        else:
            continue;

    for user in game['users']:
        emit("message",{'text':user+' is picking a word', 'gamenumber':data['gamenumber'],'username':'Server'}, to=room)

        emit("wordtransport",{'words':choosewords(),'userdrawing':user}, to=room)

        secondswaittime = game['drawduration']

        global timerover
        timerover = False

        @socketio.on('wordchosen')
        def chooseword(data):
            
            game['word'] = data['word']
            game['users'][user]['drawing'] = True

            emit("message",{'text':user+' is drawing', 'gamenumber':data['gamenumber'],'username':'Server'}, to=room)

            for i in range(1,secondswaittime+1):
                emit("timer",{'time':secondswaittime-i,'gamenumber':data['gamenumber']}, to=room)
                socketio.sleep(1)

            global timerover
            timerover = True
            game['users'][user]['drawing'] = False
        
        while timerover==False:
            socketio.sleep(1)

        emit("wordwas",{'data':game}, to=room)
    
    emit('gameover',{'stats':game['users']}, to=room)
    print(game)

@socketio.on('message')
def on_message(data):
    for game in games:
        if int(data['gamenumber'])==(game['gamenumber']):  
            print(data)
            if (data['text']).lower() == game['word'].lower(): 
                game['users'][(data['username'])]['score'] = game['users'][(data['username'])]['score'] + 1
                for user in game['users']:
                    if game['users'][user]['drawing']:
                        game['users'][user]['score'] = game['users'][user]['score'] + 1
                emit("message",{'text':data['username']+' got the word', 'gamenumber':data['gamenumber'],'username':'Server', 'gottheword':True}, to=data['gamenumber'])
            else:
                emit("message", data, to=data['gamenumber'])
            break;
        else:
            continue;

@socketio.on('imagetransport')
def handle_message(data):
    print('received image')
    emit("imagetransport", data, to=data['gamenumber'])

if __name__ == '__main__':
    print("running")
    socketio.run(app,port=5001, host="0.0.0.0")
