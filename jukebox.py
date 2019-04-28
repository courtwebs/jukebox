import tornado.ioloop
import tornado.web
import os

import queues
import player
import downloader
import status

NUM_DOWNLOAD_THREADS = 5
YOUTUBE_PREFIX = "https://www.youtube.com/watch?v="
SONG_LIBRARY_DIR = "library"

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        page = self.make_add_song_form() + "<br><br>" + self.get_now_playing() + "<br><br>" + self.get_playlist()
        self.write(page)

    def make_add_song_form(self):
        form = """
        <form>
        Song URL: 
        <input type="text" name="song">
        <input type="submit" action="/queue">
        </form>
        """
        return form
        """To add a song to the queue:
        <pre>
        wget localhost:8888/queue/id
        </pre>

        where id is the unique identifier of the youtube video you want to pull the audio from.
        E.g., for the url `https://www.youtube.com/watch?v=JJ9IX4zgyLs`, the id is `JJ9IX4zgyLs`.
        """

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
        (r"/(.*)", DebugHandler),
    ])

if __name__ == "__main__":
    os.chdir(os.getcwd() + os.sep + SONG_LIBRARY_DIR)
    # One player thread to rule them all
    playthread = player.PlayThread()
    playthread.start()

    # Multiple download threads for concurrent downloads
    for i in range(NUM_DOWNLOAD_THREADS):
        downloadthread = downloader.DownloadThread()
        downloadthread.start()

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
