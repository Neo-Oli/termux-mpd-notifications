#!/usr/bin/env python
import argparse
import sys
import os
import subprocess
from mpd import MPDClient
import mpd
import time
import shutil
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
        parser.description="Displays a Notification in Termux with the currently playing Track in MPD and media controls"
        parser.add_argument('--host', help='Host')
        parser.add_argument('--port', default="6600", help='Port')
        options = parser.parse_args()


        self.client=MPDClient()
        self.notificationId="termux-mpd-notification"
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
            self.music_dir=self.client.listmounts()[0]['storage']
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
        for attr in ["album","artist","title","file"]:
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
        dirname=os.path.dirname("{}/{}".format(self.music_dir,metadata["file"]))
        artpath=""
        for segment in ["/", "/../"]:
            for filename in ["cover.jpg", "cover.jpeg", "cover.png"]:
                check_art="{}{}{}".format(dirname,segment,filename)
                if os.path.exists(check_art):
                    artpath=check_art
                    break
            if artpath:
                break
        tmpart=""
        if artpath:
            # Sometimes the art may not be available to the api, for example if it is within a mount
            tmpart="{}/termux-mpd-notification-cover".format(os.environ['TMPDIR'])
            shutil.copy(artpath,tmpart)
        command=[
            "termux-notification",
            "--id", self.notificationId,
            "--title", title,
            "--content", "{}, {}".format(metadata["artist"], metadata["album"]),
            "--type", "media",
            "--media-previous","mpc prev {}".format(self.mpcinfo),
            "--media-pause","mpc pause {}".format(self.mpcinfo),
            "--media-play","mpc play {}".format(self.mpcinfo),
            "--media-next","mpc next {}".format(self.mpcinfo),
            "--on-delete", "mpc stop {}".format(self.mpcinfo),
            "--image-path", tmpart,
        ]
        output=subprocess.call(command)
def main(args=None):
    if args is None:
        args = sys.argv[1:]
    termuxmpdnotifications(args)
if __name__ == "__main__":
    main()


