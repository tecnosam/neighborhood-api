import pandas as pd

from db.mysql import Connection

from account_api import User

# app = current_app( app )

class Chats:
    def __init__( self, uid, db = Connection() ):
        self.uid = uid
        self.db = db
    
    def load_messages( self ):
        print(self.uid)
        sql = f"SELECT * FROM chats WHERE (`uid`='{self.uid}' OR `msgTo`='{self.uid}') ORDER BY `id` DESC";
        data = pd.read_sql( sql, self.db.db )
        return data

    def load_threads( self ):
        data = self.load_messages()
        # print( data )
        threads = dict()
        key = lambda x: x['uid'] if x['uid'] != self.uid else x['msgTo']
        for i in range( data.shape[0] ):
            msg = data.loc[ i ]
            uid = key( msg )

            if ( uid in threads ):
                threads[ uid ]['messages'].append( eval(msg.to_json()) )
            else:
                ud = User.info( uid )
                # print( msg.to_dict() )

                threads[ uid ] = {
                    "uid": uid,
                    "messages": [ eval( msg.to_json() ) ],
                    "room": f"{self.uid}-{uid}" if self.uid < uid else f"{uid}-{self.uid}",
                    **ud
                }
# snowden
        return list( threads.values() )
    
    def store_msg( self, msg ):
        keys = str( tuple( msg.keys() ) ).replace("'", "`")
        vals = str( tuple( msg.keys() ) )

        sql = f"INSERT INTO chats {keys} VALUES {vals}"

        return self.db.set( sql )

    def del_msg( self, id ):
        sql = f"DELETE FROM chats WHERE `id`={id} AND `uid`='{self.uid}'"
