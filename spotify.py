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
    current_track = ''
    track_vote_skip = set()

    def activate(self):

         self.restore_store()
         super(spotify, self).activate()
         self.start_poller(3, self.send_current_track)

    def send_current_track(self):
        
        self.restore_store()
        current_track = self.get_current_track()
        # print "current_store: ", global_store
        # print "current_track: ", current_track

        if current_track != self.current_track:

            # print "\n\n\n\n running callback \n\n\n"

            self.send(
                self.channel,
                # str(msg.frm).split('/')[0], # tbd, find correct mess.ref 
                "Current track: %s" % current_track,
                message_type="groupchat"#msg.type
            )

            # global_store['current_track'] = current_track
            self.current_track = current_track
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

    def next_track(self):
        p = subprocess.Popen(['/usr/bin/osascript', 'plugins/err-spotify/nextTrack.scpt'], stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()
        p.stdout.close()
        return stdout

    def get_current_track(self):
        p = subprocess.Popen(['/usr/bin/osascript', 'plugins/err-spotify/currentTrack.scpt'], stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()
        p.stdout.close()
        return stdout

    @botcmd()
    def track_skip(self, msg, args):
        # say_vote_threashold
        self.track_vote_skip.add(msg.nick)
        if len(self.track_vote_skip) >= 3:
            # self.track_vote_skip = "On"
            self.next_track()
            self.track_vote_skip = set()
  
            return "Vote passed.  Skipping to the next track." 
        return "Current vote to skip next track: %d" % len(self.track_vote_skip)



    @botcmd()
    def track(self, msg, args):

        global_store['current_track'] = self.get_current_track()
        self.save_store()
        return "Now playing: %s" % global_store['current_track']
