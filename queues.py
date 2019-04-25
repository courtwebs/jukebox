from collections import dequeue
from threading import Lock

download_queue = dequeue()
play_queue = dequeue()
download_lock = Lock()
play_lock = Lock()
