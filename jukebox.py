import tornado.ioloop
import tornado.web
import queues
import player
import downloader

NUM_DOWNLOAD_THREADS = 5

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        page = self.make_add_song_form() + "<br><br>" + self.get_playlist()
        self.write(page)

    def make_add_song_form(self):
        return """To add a song to the queue:
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

class RemoveSongHandler(tornado.web.RequestHandler):
    def post(self, song_index):
        play_lock.acquire()

        try:
            song_name = play_queue[int(song_index)]
            del queues.play_queue[int(song_index)]
        except:
            print("Unable to remove song at index " + str(song_index))
        finally:
            queues.play_lock.release()

        print("Removed song '" + str(song_name) + "' at index '" + str(song_index) + "'\n")
        self.write("Removed song '" + str(song_name) + "' at index '" + str(song_index) + "'\n")

class QueueHandler(tornado.web.RequestHandler):
    def get(self, video_id):
        self.sanitize(video_id)

        queues.download_lock.acquire()

        try:
            url = "https://www.youtube.com/watch?v=" + str(video_id)
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

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/queue/(.*)", QueueHandler)
    ])

if __name__ == "__main__":
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
