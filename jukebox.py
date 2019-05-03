import tornado.ioloop
import tornado.web
import os

import queues
import player
import downloader
import speak
import status

NUM_DOWNLOAD_THREADS = 5
YOUTUBE_PREFIX = "https://www.youtube.com/watch?v="
SONG_LIBRARY_DIR = "library"

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        page = self.get_now_playing() + "<br><br>" + self.get_playlist() + "<br><br>" + self.make_instructions() 
        self.write(page)

    def make_instructions(self):
        form = """<h1>Controlling The Jukebox</h1>
        I'm terrible at web development, so you won't find any buttons that do stuff. Everything is controlled through GET requests. Here's what you can do:

        <h2>Add a song to the queue by YouTube URL</h2>
        
        To add a song to the queue:
        <pre>
        wget jukebox:8888/queue/id
        </pre>

        where id is the unique identifier of the youtube video you want to pull the audio from.
        E.g., for the url "https://www.youtube.com/watch?v=JJ9IX4zgyLs", the id is "JJ9IX4zgyLs".

        Alternatively, you can add an already downloaded song to the queue via the library.

        <h2>Add a song to the queue from the library</h2>

        To list the songs in the library, navigate to:

        <pre>
        jukebox:8888/library
        </pre>

        To play a song from the library:

        <pre>
        wget jukebox:8888/play/id
        </pre>

        where id is the song's position in the list. E.g. if the library looks like this:

        <pre>
        1. Rick Astley - Never Gonna Give You Up (Video)-dQw4w9WgXcQ.m4a
        2. Tom Jones - 'It's Not Unusual' (With Lyrics)-kWvbJsB0OBc.m4a
        3. Tom Jones - Whats New Pussycat - Lyrics-Ga3I5DTIA-E.m4a
        4. Nyan Cat [original]-QH2-TGUlwu4.m4a
        </pre>

        and you'd like to play "What's New Pussycat", then:

        <pre>
        wget jukebox:8888/play/3
        </pre>

        <h2>Remove a song from the queue</h2>

        To remove a song from the queue:

        <pre>
        wget jukebox:8888/del/id
        </pre>

        where id is the song's position in the playlist.
        <h2>Make it talk</h2>
        To make the jukebox talk:

        <pre>
        wget jukebox:8888/speak/your_sentence_with_underscores
        </pre>
        """

        return form

    def get_playlist(self):
        playlist = "Playlist:<br>"

        if len(queues.play_queue) == 0:
            playlist += "Playlist is empty"
        else:
            playlist += "<ol>\n"

            for i in range(len(queues.play_queue)):
                playlist += "<li> " + str(queues.play_queue[i]) + "</li>\n"

            playlist += "</ol>\n"

        return playlist

    def get_now_playing(self):
        now_playing = "Now playing: " + str(status.now_playing)
        return now_playing

class RemoveSongHandler(tornado.web.RequestHandler):
    def get(self, song_index):
        queues.play_lock.acquire()

        try:
            list_index = int(song_index) - 1
            song_name = queues.play_queue[list_index]
            del queues.play_queue[list_index]
            print("Removed song '" + str(song_name) + "' at index '" + str(song_index) + "'\n")
            self.write("Removed song '" + str(song_name) + "' at index '" + str(song_index) + "'\n")
        except:
            print("Unable to remove song at index " + str(song_index))
        finally:
            queues.play_lock.release()

class QueueHandler(tornado.web.RequestHandler):
    def get(self, video_id):
        self.sanitize(video_id)

        queues.download_lock.acquire()

        try:
            url = YOUTUBE_PREFIX + str(video_id)
            queues.download_queue.append(str(url))
            self.write("Added URL '" + str(url) + "' to the download queue.\n")
        except:
            print("Unable to queue download url '" + str(url) + "'\n")
            self.write("Unable to add URL '" + str(url) + "' to the download queue.\n")
        finally:
           queues.download_lock.release()

    def sanitize(self, s):
        """
        Sanitize s such that it can be included in a command run on the command line
        and _probably_ not cause any harm.
        """

        # Our input shouldn't contain spaces
        s = "".join(s.split())

        return s

class LibraryHandler(tornado.web.RequestHandler):
    def get(self):
        page = "Library:<br><ol>"

        songs = os.listdir()

        for song in songs:
            page += "<li>" + str(song) + "</li>"

        page += "</ol>"

        self.write(page)

class PlayHandler(tornado.web.RequestHandler):
    def get(self, song_id):
        """Queues an already downloaded song from the library"""

        # This is the dumbest way we could do this. This should return songs in the same 
        # order every time. But, if a song download is initiated between when the user 
        # looked up the library and made the request to play a song from the library, it's 
        # going to shift the indices of some of the songs in the library, and we'll end up 
        # playing the wrong song.
        songs = os.listdir()

        # This might be a bad idea. In theory, the player thread should never hold the 
        # play lock for more than an instant. But... if it does hold it for a long time,
        # it's going to DoS the main thread serving requests because of this.
        queues.play_lock.acquire()

        try:
            list_id = int(song_id) - 1
            queues.play_queue.append(songs[list_id])
            print("Added song '" + str(songs[list_id]) + "' to the play queue")
            self.write("Added song '" + str(songs[list_id]) + "' to the play queue")
        except:
            print("Unable to queue song at library index '" + str(song_id) + "'")
            self.write("Unable to queue song at library index '" + str(song_id) + "'")
        finally:
            queues.play_lock.release()

class SpeakHandler(tornado.web.RequestHandler):
    def get(self, sentence):
        sentence = sentence.replace('_', ' ')
        queues.speak_lock.acquire()

        try:
            queues.speak_queue.append(sentence)
            print("Added speech '" + sentence + "' to the speak queue")
        except:
            print("Unable to add speech '" + setnence + "' to the speak queue")
        finally:
            queues.speak_lock.release()

class DebugHandler(tornado.web.RequestHandler):
    def get(self, args):
        print("Debug handler received args = " + str(args))

    def post(self, args):
        print("Debug handler received args = " + str(args))

    def put(self, args):
        print("Debug handler received args = " + str(args))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/queue/(.*)", QueueHandler),
        (r"/del/(.*)", RemoveSongHandler),
        (r"/library", LibraryHandler),
        (r"/play/(.*)", PlayHandler),
        (r"/speak/(.*)", SpeakHandler),
        (r"/(.*)", DebugHandler),
    ])

if __name__ == "__main__":
    os.chdir(os.getcwd() + os.sep + SONG_LIBRARY_DIR)
    # One player thread to rule them all
    playthread = player.PlayThread()
    playthread.start()

    # Creating speech files shouldn't be a time consuming task,
    # so we have just the one thread
    speakthread = speak.SpeakThread()
    speakthread.start()

    # Multiple download threads for concurrent downloads
    for i in range(NUM_DOWNLOAD_THREADS):
        downloadthread = downloader.DownloadThread()
        downloadthread.start()

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
