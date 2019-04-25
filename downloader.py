import threading
import subprocess
import queues

class DownloadThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:

            # This is safe to check before the lock is acquired because this thread is the only consumer
            if len(queues.download_queue) > 0:

                queues.download_lock.acquire()

                try:
                    to_download = queues.download_queue.popleft()
                finally:
                    queues.download_lock.release()

                output = subprocess.check_output(['youtube-dl', '-f', 'm4a', to_download])
                song_name = self.get_song_name(output)

                queues.play_lock.acquire()

                try:
                    queues.play_queue.append(str(song_name))
                except:
                    print("Unable to queue song '" + str(song_name) + "'\n")
                finally:
                    queues.play_lock.release()

            time.sleep(0) # yield execution to another thread

    def get_song_name(self, output):
        matches = re.search('\[ffmpeg\] Correcting container in "(.*)"', output)

        if matches == None:
            # It's alright to return a blank song - when it gets added to the queue, omxplayer will just 
            # try to play nothing, quit, and things will go on fine
            songname = ""
        else:
            songname = matches.group(1)

        return songname
