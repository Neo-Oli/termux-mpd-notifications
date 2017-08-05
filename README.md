#Termux-mpd-notification

This is an companion program for mpd on [Termux](http://termux.com). It displays a notification with media controls.

![Screenshot](/Screenshots/Notification-Media-Controls-small.png)

## Requirements

* [Termux:API](https://play.google.com/store/apps/details?id=com.termux.api) App from Google Play 

### Packages: 

* `termux-api`
* `python`
* `mpd`
```
apt install termux-api python mpd
```

## Installation

```
pip install git+https://github.com/Neo-Oli/termux-mpd-notifications
```

## Usage

While `termux-mpd-notification` runs, notifications for playing music in `mpd` will be shown. I suggest running it as a [service](https://github.com/Neo-Oli/termux-services/)


## See also

https://github.com/Neo-Oli/termux-mpv for notifications for mpv
