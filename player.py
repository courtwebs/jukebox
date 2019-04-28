import threading
import subprocess
import queues
import time
import status

OUTPUT_DEVICE = 'local'

class PlayThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:

            # This is safe to check before the lock is acquired because this thread is the only consumer
            if len(queues.play_queue) > 0:
                queues.play_lock.acquire()

                try:
                    song = queues.play_queue.popleft()
                finally:
                    queues.play_lock.release()

                print("Playing song '" + str(song))
                status.now_playing = song
                
                try:
                    subprocess.check_output(['omxplayer', '-o', OUTPUT_DEVICE, song])
                except:
                    print("Unable to play song '" + song)

                status.now_playing = ""

            time.sleep(0) # yield execution to another thread
