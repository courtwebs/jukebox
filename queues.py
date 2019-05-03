from collections import deque
from threading import Lock

download_queue = deque()
play_queue = deque()
speak_queue = deque()
download_lock = Lock()
play_lock = Lock()
speak_lock = Lock()
