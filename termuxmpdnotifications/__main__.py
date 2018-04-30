#!/usr/bin/env python
import argparse
import sys
import os
import subprocess
from mpd import MPDClient
import mpd
import time
import argparse
import signal
class termuxmpdnotifications:
    def cleanup(self,signum,frame):
        self.removeNotification()
        try:
            self.client.close()
        except:
            pass
    def __init__(self,args):
        # atexit.register(self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
        self.visible=False
        parser = argparse.ArgumentParser()
        parser.description="Best viewed when piped into `less -RS`"
        parser.add_argument('--host', help='Host')
        parser.add_argument('--port', default="6600", help='Port')
        options = parser.parse_args()


        self.client=MPDClient()
        self.notificationId=str(time.time())
        if options.host:
            self.host=options.host
        elif 'MPD_HOST' in os.environ:
            self.host=os.environ['MPD_HOST']
        else:
            self.host="localhost"
        self.port=options.port
        self.mpcinfo="-h {} -p {}".format(self.host,self.port)
        try:
            self.client.connect(self.host,self.port)
            self.err("Connected to MPD Version {}".format(self.client.mpd_version))
            while True:
                self.status=self.client.status()
                self.metadata=self.client.currentsong()
                if self.status["state"]=="stop":
                    self.removeNotification()
                else:
                    self.updateNotification()
                self.client.idle()
        except mpd.ConnectionError:
            self.err("Connection Aborted.")
            self.removeNotification()
        except ConnectionRefusedError:
            self.err("Connection Refused.")
            self.removeNotification()
    def err(self,out):
        print(out,file=sys.stderr)
    def removeNotification(self):
        if self.visible==True:
            self.visible=False
            command=["termux-notification-remove",self.notificationId]
            output=subprocess.call(command)
        self.updatehook()
    def updatehook(self):
        command="~/bin/hook-update-mpd"
        devnull=open(os.devnull, 'wb')
        try:
            subprocess.call(["sh", "-c", command],stdout=devnull,stderr=devnull)
        except:
            pass
    def updateNotification(self):
        self.updatehook()
        self.visible=True
        # padding="           "
        #disable padding for now
        padding=""
        # playbutton="{}⏸{}".format(padding,padding)
        # prevbutton="{}⏮{}".format(padding,padding)
        # nextbutton="{}⏭{}".format(padding,padding)
        playbutton="{}❙❙{}".format(padding,padding)
        prevbutton="{}|◀◀{}".format(padding,padding)
        nextbutton="{}▶▶|{}".format(padding,padding)
        if self.status["state"] == "pause":
            playbutton="{} ▶ {}".format(padding,padding)
        metadata={}
        for attr in ["album","artist","title"]:
            try:
                metadata[attr]=self.metadata[attr]
            except KeyError:
                try:
                    metadata[attr]=self.metadata[attr.upper()]
                except KeyError:
                    metadata[attr]="None"
        if metadata["title"]=="None":
            title="Unknown"
        else:
            title=metadata["title"]
        command=[
            "termux-notification",
            "--id", self.notificationId,
            "--title", title,
            "--content", "{}, {}".format(metadata["artist"], metadata["album"]),
            "--priority", "max",
            # "--action", ";".join([
                # "am start --user 0 -n com.termux/com.termux.app.TermuxActivity",
                # "echo 'updateNotification'> {}".format(self.fifoname)
                # ]),
            "--button1", prevbutton,
            "--button1-action","mpc prev {}".format(self.mpcinfo),
            "--button2", playbutton,
            "--button2-action","mpc toggle {}".format(self.mpcinfo),
            "--button3", nextbutton,
            "--button3-action","mpc next {}".format(self.mpcinfo),
            "--on-delete", "mpc stop {}".format(self.mpcinfo),
        ]
        output=subprocess.call(command)
def main(args=None):
    if args is None:
        args = sys.argv[1:]
    termuxmpdnotifications(args)
if __name__ == "__main__":
    main()


