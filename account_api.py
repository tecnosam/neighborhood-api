from db.mysql import Connection
import sys, os, hashlib, time

class User:
    def __init__(self, obj = Connection()):
        self.obj = obj

    def create( self, name, email, pwd ):
        pwd = hashlib.md5( pwd.encode() ).hexdigest()
        uid = hashlib.md5( f"{email}-{time.time()}".encode() ).hexdigest()
        sql = """
                    INSERT INTO users (`uid`, name, email, pwd)
                    VALUES
                    ( '%s', '%s', '%s', '%s' )
            """ % (uid, name, email, pwd)
        # obj = Connection()
        return self.obj.set( sql )

    def login( self, email, pwd ):
        _pwd = hashlib.md5( pwd.encode() ).hexdigest()
        sql = f"""
                    SELECT * FROM users WHERE email='{email}' AND pwd='{_pwd}'
            """
        if (self.obj.check( sql )):
            dat = list(self.obj.getone( sql ))
            cols = ['uid', 'name', 'email', 'pwd', 'bio', 'imageURL', 'dfe', 'date-created', 'q-index']
            res = dict()
            while True:
                try:
                    res[ cols.pop() ] = dat.pop()
                except IndexError:
                    break
            res['pwd'] = pwd
            return res
        else:
            return False

    def ChangeAttr( self, node, val, uid ):

        if (node == 'pwd'):
            val = hashlib.md5( val.encode() ).hexdigest()
        elif ( node in ['uid', 'mid', 'id'] ):
            return False
        if ( type( val ) == str ):
            val = val.replace('\\', '\\\\').replace('\"', '\\\"').replace( '\'', "\\\'" )
        sql = "UPDATE users SET `%s`='%s' WHERE `uid`='%s'" % ( node, val, uid )
        # obj = Connection()
        return self.obj.set( sql )

    def ChangeMultiple( self, data, uid ):
        for i in data:
            try:
                self.ChangeAttr( i, data[ i ], uid )
            except:
                continue
        return True

    @staticmethod
    def name(uid):
        db = Connection()
        sql = f"SELECT `name` FROM users WHERE `uid`='{uid}'"
        return db.getone( sql )[0]

    @staticmethod
    def info(uid, adapter = Connection()):
        sql = f"SELECT `name`,`bio`,`imageURL`,`dfe` FROM users WHERE `uid`='{uid}'"

        cols = ['name','bio','imageURL','dfe']

        dat = list(adapter.getone( sql ))
        print(dat)

        res = dict()

        while True:
            try:
                res[ cols.pop() ] = dat.pop()
            except IndexError:
                break

        return res
    
    def load_neighbors(self, uid, dfe):
        sql = f"""SELECT `name`,`bio`,`imageURL`,`dfe` FROM users WHERE 
            `uid`!='{uid}' AND dfe<={dfe}+10 AND dfe>={dfe}-10 ORDER BY dfe ASC"""


        dat = self.db.get( sql )
        print(dat)

        ret = list()
        for i in range(len(dat)):
            cols = ['name','bio','imageURL','dfe']
            row = list( dat[i] )
            res = dict()
            while True:
                try:
                    res[ cols.pop() ] = row[i].pop()
                except IndexError:
                    break
            
            ret.append( res )

        return ret

if __name__ == '__main__':
    obj = User()
    print( obj.create( "Samuel Abolo", "ikabolo59@gmail.com", "fish" ) )
    print( obj.create( "Samuel Abolo", "ikabolo59@gmail.com", "fish" ) )
    print( obj.login( "ikabolo59@gmail.com", "fish" ) )
    print( obj.ChangeAttr( 'bio', "Official Neighborhood account of Abolo Samuel", '641dff486486b932ed35c833e91ab8af' ) )
    print( User.info( '641dff486486b932ed35c833e91ab8af' ) )
    print( User.name( '641dff486486b932ed35c833e91ab8af' ) )