import os
import traceback

from helpers import safe_print

from bootstrap import initialize

from command_processor import handle_command

from scheduler import (
    shutdown_event,
    set_current_thread_priority,
    THREAD_PRIORITY_ABOVE_NORMAL,
)

from sound import play_shutdown_sound


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    set_current_thread_priority(
        THREAD_PRIORITY_ABOVE_NORMAL
    )

    scheduler = None

    try:

        scheduler, microphone = initialize()

        while not shutdown_event.is_set():

            try:

                command = microphone.listen_once()

                if command:

                    handle_command(
                        scheduler,
                        command
                    )

                while (
                    scheduler.is_busy()
                    and
                    not shutdown_event.is_set()
                ):

                    scheduler.wait_for_state_change(
                        timeout=1
                    )

            except KeyboardInterrupt:

                raise

            except Exception:

                safe_print(
                    "[main] Unexpected Error"
                )

                traceback.print_exc()

    except KeyboardInterrupt:

        safe_print(
            "\n[main] Shutdown Requested"
        )

    finally:

        try:

            # play_shutdown_sound()
            safe_print(f"{'='* 5}SHUTTING DOWN{'='* 5}")

        except Exception:

            pass

        if scheduler:

            try:

                scheduler.shutdown(
                    wait=False
                )

            except Exception as e:

                safe_print(
                    f"[shutdown] {e}"
                )

        safe_print()
        safe_print("=" * 60)
        safe_print("JARVIS OFFLINE")
        safe_print("=" * 60)

        os._exit(0)