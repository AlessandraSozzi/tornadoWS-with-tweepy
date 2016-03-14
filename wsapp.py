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
# Refer to https://dev.twitter.com/oauth/overview/application-owner-access-tokens
APP_NAME = ''
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''




class WSHandler(tornado.websocket.WebSocketHandler):
    
    connections = []
    
    def check_origin(self, origin):
        return True

    def open(self):
        print 'Connection established.'
        self.connections.append(self)

        
    
    # When message arrives write it to websocket
    def on_message(self, message):
        print 'Tweet received: \"%s\"' % message
        self.write_message(message)
        
           
    def on_close(self):
        print 'Conn closed...'
        self.connections.remove(self)



class MyStreamListener(tweepy.StreamListener, WSHandler):

    # tweet handling - Extract text and and write message
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
    stream = tweepy.Stream(auth, MyStreamListener()) 
    # Accept tweets that use #dataviz hashtag
    stream.filter(track=['#dataviz'])  

if __name__ == "__main__":

    threading.Thread(target=OpenStream).start()
    application = tornado.web.Application([
        (r'/ws', WSHandler),
        (r'/(favicon.ico)', tornado.web.StaticFileHandler, {'path': 'favicon.ico'}) # path to your icon
    ])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()