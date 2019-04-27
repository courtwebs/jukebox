import threading
import subprocess
import queues
import time
import re

class DownloadThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            download_url = self.get_next_download()

            if download_url is not None:
                dl_output = self.download_song(download_url)

                if dl_output is not None:
                    song_name = self.get_song_name(dl_output)

                    if song_name is not None:
                        print("Adding " + str(song_name) + " to the play queue")
                        self.queue_song(song_name)

            time.sleep(0) # yield execution to another thread

    def queue_song(self, song):
        queues.play_lock.acquire()

        try:
            queues.play_queue.append(str(song))
        except:
            print("Unable to queue song '" + str(song) + "'\n")
        finally:
            queues.play_lock.release()

    def get_next_download(self):
        download_url = None
        queues.download_lock.acquire()

        try:
            if len(queues.download_queue) > 0:
                download_url = queues.download_queue.popleft()
        finally:
            queues.download_lock.release()

        return download_url

    def download_song(self, url):
        print("Downloading song from " + str(url))

        try:
            output = subprocess.check_output(['youtube-dl', '-f', 'm4a', url])
        except:
            print("Unable to download song from '" + url)
            return None

        return output

    def get_song_name(self, output):
        output = output.decode('ascii')
        matches = re.search('\[ffmpeg\] Correcting container in "(.*)"', str(output))

        if matches == None:
            songname = None
        else:
            songname = matches.group(1)

        return songname
