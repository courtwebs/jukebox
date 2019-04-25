import threading
import subprocess
import queues
import time.sleep

class PlayThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:

            # This is safe to check before the lock is acquired because this thread is the only consumer
            if len(queues.play_queue) > 0:
                queues.play_lock.acquire()

                try:
                    to_play = queues.play_queue.popleft()
                finally:
                    queues.play_lock.release()
                    
                subprocess.check_output(['omxplayer', '-o', 'alsa', to_play])

            time.sleep(0) # yield execution to another thread
