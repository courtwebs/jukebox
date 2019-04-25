# Jukebox!
This is a little jukebox you can run on your raspberry pi that accepts youtube video slugs, downloads the music, and plays it.
You might wonder why you'd want something like this.
I don't know why YOU would - but I used it to prank my office coworker by connecting my pi3 to their bluetooth speakers and handing control of this little jukebox off to everyone else in the office.

## Installing this thing
Clone the repo, then install the dependencies:

```
sudo apt install ffmpeg python3-pip
pip3 install youtube-dl
```

## Running this thing
```
python3 jukebox.py
```

## Controlling the thing
You can do two things - you can retrieve the current play queue, or you can queue up a new song.

Getting the current play queue:
```
wget localhost:8888
```

Queuing up a new song:
```
wget localhost:8888/queue/<uri>
```

where `<uri>` is the unique identifier of the youtube video you want to pull the audio from.
E.g., for the url `https://www.youtube.com/watch?v=JJ9IX4zgyLs`, the uri is `JJ9IX4zgyLs`.

Obviously, unless your firewall is blocking it, you should be able to control your little jukebox from another PC by replacing `localhost` with your pi's IP (or hostname, if you have local DNS).
