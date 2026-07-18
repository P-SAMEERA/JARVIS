import queue
import threading
import itertools
import traceback
import concurrent.futures
import sys

from helpers import (
    safe_print,
    sanitize_text,
)

from speech import speak

IS_WINDOWS = sys.platform.startswith("win")

THREAD_PRIORITY_BELOW_NORMAL = -1
THREAD_PRIORITY_ABOVE_NORMAL = 1

# ============================================================
# Thread Priority
# ============================================================



def set_current_thread_priority(level: int):

    if not IS_WINDOWS:
        return

    try:

        import ctypes

        handle = ctypes.windll.kernel32.GetCurrentThread()

        ctypes.windll.kernel32.SetThreadPriority(
            handle,
            level
        )

    except Exception as e:

        safe_print(f"[priority] {e}")


# ============================================================
# Priority Scheduler
# ============================================================

class PriorityScheduler:

    def __init__(self, max_workers=3):

        self.queue = queue.PriorityQueue()

        self.counter = itertools.count()

        self.pending = 0

        self.pending_lock = threading.Lock()

        self.speak_lock = threading.Lock()

        self.running = True

        self.mic_listener = None

        self.state_changed = threading.Event()

        self.executor = concurrent.futures.ThreadPoolExecutor(

            max_workers=max_workers,

            thread_name_prefix="jarvis-worker"

        )

        self.dispatcher = threading.Thread(

            target=self._dispatch_loop,

            daemon=True,

            name="jarvis-dispatcher"

        )

        self.dispatcher.start()


    # ========================================================
    # Queue State
    # ========================================================

    def register_pending(self):

        with self.pending_lock:

            self.pending += 1

            became_busy = self.pending == 1

        if became_busy:

            self.state_changed.set()

        return self.pending


    def task_completed(self):

        with self.pending_lock:

            self.pending -= 1

            became_idle = self.pending == 0

        if became_idle:

            self.state_changed.set()


    def is_busy(self):

        with self.pending_lock:

            return self.pending > 0


    def wait_for_state_change(self, timeout=None):

        fired = self.state_changed.wait(timeout)

        if fired:

            self.state_changed.clear()

        return fired


    # ========================================================
    # Submit Tasks
    # ========================================================

    def submit(

        self,

        priority,

        function,

        *args,

        **kwargs

    ):

        pending = self.register_pending()

        safe_print(

            f"[scheduler] queued "

            f"(priority={priority}, pending={pending})"

        )

        self.queue.put(

            (

                priority,

                next(self.counter),

                function,

                args,

                kwargs

            )

        )


    def run_now(

        self,

        function,

        *args,

        **kwargs

    ):

        pending = self.register_pending()

        safe_print(

            f"[scheduler] "

            f"executing immediately "

            f"(pending={pending})"

        )

        self.executor.submit(

            self._execute,

            function,

            args,

            kwargs

        )


    # ========================================================
    # Dispatcher
    # ========================================================

    def _dispatch_loop(self):

        set_current_thread_priority(

            THREAD_PRIORITY_BELOW_NORMAL

        )

        while self.running:

            try:

                priority, _, function, args, kwargs = self.queue.get(

                    timeout=0.5

                )

            except queue.Empty:

                continue

            self.executor.submit(

                self._execute,

                function,

                args,

                kwargs

            )


    def _execute(

        self,

        function,

        args,

        kwargs

    ):

        set_current_thread_priority(

            THREAD_PRIORITY_BELOW_NORMAL

        )

        try:

            function(

                *args,

                **kwargs

            )

        except Exception as e:

            safe_print(

                f"[scheduler] {e}"

            )

            traceback.print_exc()

        finally:

            self.task_completed()


    # ========================================================
    # Speech
    # ========================================================

    def speak_safe(self, text: str):

        text = sanitize_text(text)

        with self.speak_lock:

            if self.mic_listener:

                self.mic_listener.pause()

            try:

                speak(text)

            finally:

                if self.mic_listener:

                    self.mic_listener.resume()


    # ========================================================
    # Shutdown
    # ========================================================

    def shutdown(self, wait=True):

        self.running = False

        self.executor.shutdown(

            wait=wait,

            cancel_futures=True

        )


# ============================================================
# Global Shutdown Event
# ============================================================

shutdown_event = threading.Event()
