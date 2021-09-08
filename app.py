from flask import Flask, render_template, send_from_directory, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from werkzeug import datastructures
from random import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

games = [
    {'users':{'bob':{'score':10,'drawing':False},'james':{'score':10,'drawing':False}},'gamenumber':23, 'gamehostusername':'bob', 'closed':False}
]

def generateandchecknumber():
    number = int(1000000*random())
    for game in games:
        if (game['gamenumber'])==number:
            print("hey")
            generateandchecknumber()
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
        games.append({'users':{},'gamenumber':gamecode, 'gamehostusername':data['hostusername'], 'closed':False})
        #return render_template('gamehost.html', data=request.form.to_dict())
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
        emit("wordtransport",{'words':['Cat','Dog','Mouse'],'userdrawing':user}, to=room)

@socketio.on('message')
def on_message(data):
    emit("message", data, to=data['gamenumber'])

@socketio.on('imagetransport')
def handle_message(data):
    print('received image')
    emit("imagetransport", data, to=data['gamenumber'])

if __name__ == '__main__':
    print("running")
    socketio.run(app,use_reloader=True)
