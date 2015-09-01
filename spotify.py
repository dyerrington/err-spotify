from errbot import BotPlugin, botcmd, webhook, logging
import pandas as pd
from collections import defaultdict
from errbot.templating import tenv
import webserver, subprocess

import subprocess, re

global_store = defaultdict() # had some problems with context, will refactor

class spotify(BotPlugin):

    store_file = 'plugins/err-spotify/spotify.cache'
    channel = "dyerrington@chat.livecoding.tv"
       
    def activate(self):

         self.restore_store()
         super(spotify, self).activate()
         self.start_poller(3, self.send_current_track)

    def send_current_track(self):
        
        self.restore_store()
        current_track = self.get_current_track()
        # print "current_store: ", global_store
        # print "current_track: ", current_track

        if current_track != global_store['current_track']:

            # print "\n\n\n\n running callback \n\n\n"

            self.send(
                self.channel,
                # str(msg.frm).split('/')[0], # tbd, find correct mess.ref 
                "Current track: %s" % current_track,
                message_type="groupchat"#msg.type
            )

            global_store['current_track'] = current_track
            self.save_store()

    def restore_store(self):
        try:
            store = pd.read_pickle(self.store_file)
            for key, value in store.iloc[0].to_dict().items():
                global_store[key]   =   value
        except:
            self.save_store()
        # print "Restoring!!!!     ", global_store

    def save_store(self):
        # print 'saving', store.head()
        print "attempting to save store: ", global_store
        store = pd.DataFrame(global_store, index=global_store.keys())
        print "our store is:", store.head()
        store.to_pickle(self.store_file)

    def get_current_track(self):
        p = subprocess.Popen(['/usr/bin/osascript', 'plugins/err-spotify/currentTrack.scpt'], stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()
        p.stdout.close()
        return stdout

    @botcmd()
    def track(self, msg, args):

        global_store['current_track'] = self.get_current_track()
        self.save_store()
        return "Now playing: %s" % global_store['current_track']
