import tornado.ioloop
import tornado.web
import queues
import player
import downloader

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        queue
        for i in range(len(queues.play_queue)):
            

        self.write("Hello, world")

class QueueHandler(tornado.web.RequestHandler):
    def get(self, url):
        queues.download_lock.acquire()

        try:
            queues.download_queue.append(str(url))
        except:
            print("Unable to queue download url '" + str(url) + "'\n")
        finally:
           queues.download_lock.release()

        self.write("Added URL '" + str(url) + "' to the download queue.\n")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/queue/(.+)", QueueHandler)
    ])

if __name__ == "__main__":
    downloadthread = downloader.DownloadThread()
    playthread = player.PlayThread()

    downloadthread.start()
    playthread.start()

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
