import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from datetime import timedelta
import json
import tweepy
from tweepy import OAuthHandler
import threading

# Authentication params
APP_NAME = 'Lab1_RHUL'
CONSUMER_KEY = 'qxp5ZKUmlip9cOtWW9NMaY1O7'
CONSUMER_SECRET = 'gnEjZRy3RarVNs7f5pQBmOULmiOvt5KXCGs0UVctaVSZT6N2Oo'
ACCESS_TOKEN = '539576899-JNqTET2DdLX1mKCZmqpPJMmf51t7WfCF5Yq7bKAC'
ACCESS_TOKEN_SECRET = 'CgPLe3CBz7FkPw6YQ7yZFVoyT4q4rJjMJ2CIeTm1RoDTr'


class WSHandler(tornado.websocket.WebSocketHandler):
    
    connections = []
    
    def check_origin(self, origin):
        return True

    def open(self):
        print 'Connection established.'
        self.connections.append(self)
        #ioloop to wait for 3 seconds before starting to send data
        #tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=10), self.send_data)
        
    
    # Our function to send new (random) data for charts
    def on_message(self, message):
        print 'Tweet received: \"%s\"' % message
        self.write_message(message)
        
        #point_data = 1
        
        #print point_data
        
        #write the json object to the socket
        #self.write_message(json.dumps(status))
        
        #create new ioloop instance to intermittently publish data
        #tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=10), self.send_data)
        
           
    def on_close(self):
        print 'Conn closed...'
        self.connections.remove(self)


# new stream listener 
class StdOutListener(tweepy.StreamListener, WSHandler):
    """ A listener handles tweets are the received from the stream. 

    """

    # tweet handling
    def on_status(self, status):
        for connection in WSHandler.connections:
            connection.write_message(status.text)

    # limit handling
    def on_limit(self, status):
        print 'Limit threshold exceeded', status
    
    def on_timeout(self, status):
        print 'Stream disconnected; continuing...'  

    # error handling
    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False

def OpenStream():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    stream = tweepy.Stream(auth, StdOutListener()) 
    stream.filter(track=['#dataviz'])  

if __name__ == "__main__":

    threading.Thread(target=OpenStream).start()
    application = tornado.web.Application([
        (r'/ws', WSHandler),
        (r'/(favicon.ico)', tornado.web.StaticFileHandler, {'path': 'C:\Users\ONS-Alessandra\Downloads\testws\favicon.ico'})
    ])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()