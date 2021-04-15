from flask import *
from chat_api import *
from account_api import *
import time

from structures import haversine

from db.mysql import Connection

from flask_socketio import SocketIO, join_room, leave_room, send, emit, rooms

app = Flask(__name__)

app.secret_key = b"Change this later"

sock = SocketIO( app )


# CRUD user system code
@app.route( "/signup", methods = ['POST'] )
def signup():
    # req name, email , pwd
    return jsonify({
        'success': User().create( **request.form ) 
    })

@app.route( "/login", methods = ['GET', 'POST'] )
def login():
    if request.method == 'GET':
        if 'uid' in session:
            return jsonify( {**session} )
        print("Foo")
        return jsonify( None )

    [email, pwd] = [ request.form['email'], request.form['pwd'] ]

    res = User().login( email, pwd )
    # streamline the data returned by the POST login to just a success flag

    if res:
        for i in res:
            session[i] = res[i]

        return jsonify( {
            "success": True,
            "data": res
        } )

    return jsonify({
        "success": res,
        "data": None
    })

@app.route("/edit/usr", methods = ['POST'])
def edit_usr():
    if ( 'uid' not in session ):
        abort(404)
    cred = request.form

    ret = {'success': True, 'worked': [], 'err': []}

    obj = User()

    for i in cred:
        if ( session[i] == cred[i] ):
            continue
        res = obj.ChangeAttr( i, cred[ i ], session['uid'] )
        if ( res == True ):
            session[ i ] = cred[i]
            ret['worked'].append(i)
        elif ( res == -2 ):
            ret['err'].append(i)

    return jsonify( ret )

@app.route("/logout")
def logout():
    k = list(session.keys())
    for i in k:
        session.pop(i)

    return jsonify( True )
# end of CRUD user system code
@sock.on( "connect" )
def on_connect():
    send( "message" )
    print(f" Cool user is connected {time.time()}")

@sock.on( "disconnect" )
def on_dis():
    print( f"user disconnected at {time.time()}" )
# chat services

@app.route( "/threads", methods = ['GET'] )
def threads():
    if 'uid' not in session:
        abort( Response("Login first") )

    threads = Chats( session['uid'] ).load_threads()

    print(jsonify(threads))

    return jsonify( threads )

@sock.on("join")
def on_join(data):
    
    join_room( data['room'] )

    send( "message", f"{session['name']} has joined this chat", room = data['room'] )

    emit ( "online", { "user": session['uid'] }, room = data['room'] )

@sock.on( "leave" )
def on_leave(data):

    leave_room( data['room'] )

    send( "message", f"{session['name']} has left this chat", room = data['room'] )

    emit( "offline", { "user": session['uid'] }, room = data['room'] )

@sock.on( "msg-send" )
def msg_send(data):
    [msg, room] = [data['msg'], data['room']]

    res = Chats( msg.uid ).store_msg( msg )

    if res:
        emit( "msg-send", msg, room = room )
    else:
        emit( "spit", {'type': "error", "message": "Failed to send message. please try again later"} )

@sock.on( "msg-del" )
def msg_del(data):
    room = data['room']
    res = Chats( session['uid'] ).del_msg( data['id'] )
    if res:
        emit( "msg-del", data['id'], room = room )

# ./ chat services
# Location things
@sock.on( "neighbors" )
def load_neighbors(coords):
    dfe = haversine( {'x': 0, 'y': 0}, coords )
    user = User()
    users = user.load_neighbors( session['uid'], dfe )

    if len(users):
        emit( "neighbors", users )

        user.ChangeAttr( "dfe", dfe, session['uid'] )


if __name__ == "__main__":
    # app.run(debug = True, host = '0.0.0.0')
    sock.run( app, debug = True, host = '0.0.0.0' )