import threading
import subprocess
import queues
import time

class DownloadThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:

            # This is safe to check before the lock is acquired because this thread is the only consumer
            if len(queues.download_queue) > 0:
                dl_output = self.download_next_song()

                # This is sort of hacky.
                if dl_output == None:
                    continue

                song_name = self.get_song_name(dl_output)

                print("Adding " + str(song_name) + " to the play queue")

                self.queue_song(song_name)

            time.sleep(0) # yield execution to another thread

    def queue_song(self, song):
        queues.play_lock.acquire()

        try:
            queues.play_queue.append(str(song_name))
        except:
            print("Unable to queue song '" + str(song_name) + "'\n")
        finally:
            queues.play_lock.release()

    def download_next_song(self):
        queues.download_lock.acquire()

        try:
            download_url = queues.download_queue.popleft()
        finally:
            queues.download_lock.release()

        print("Downloading song from " + str(download_url))

        try:
            output = subprocess.check_output(['youtube-dl', '-f', 'm4a', download_url])
        except:
            print("Unable to download song from '" + download_url)
            return None

        return output

    def get_song_name(self, output):
        matches = re.search('\[ffmpeg\] Correcting container in "(.*)"', output)

        if matches == None:
            # It's alright to return a blank song - when it gets added to the queue, omxplayer will just 
            # try to play nothing, quit, and things will go on fine
            songname = ""
        else:
            songname = matches.group(1)

        return songname
