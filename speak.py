import threading
import subprocess
import queues
import time
import re

class SpeakThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.request_id = 0

    def run(self):
        while True:
            speech_text = self.get_next_speech()

            if speech_text is not None:
                self.request_id += 1
                speech_file = self.make_speech(speech_text)

                if speech_file is not None:
                    print("Adding " + str(speech_file) + " to the play queue")
                    self.queue_speech(speech_file)

            time.sleep(0) # yield execution to another thread

    def queue_speech(self, speech):
        queues.play_lock.acquire()

        try:
            queues.play_queue.append(str(speech))
        except:
            print("Unable to queue speech file '" + str(speech) + "'\n")
        finally:
            queues.play_lock.release()

    def get_next_speech(self):
        speech_text = None
        queues.speak_lock.acquire()

        try:
            if len(queues.speak_queue) > 0:
                speech_text = queues.speak_queue.popleft()
        finally:
            queues.speak_lock.release()

        return speech_text

    def make_speech(self, speech_text):
        print("Creating speech '" + str(speech_text) + "'")
        outfile = "../speeches/speech_" + str(self.request_id)

        try:
            output = subprocess.check_output(['espeak', '-w', outfile, speech_text])
        except:
            print("Unable to create speech '" + speech_texti + "'")
            return None

        return outfile

