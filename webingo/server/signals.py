import signal
import atexit

exit_handler_executed = False

def on_exit():
    global exit_handler_executed
    if exit_handler_executed:
        return

    # TODO stuff goes here

    exit_handler_executed = True

def install_signals():
    signal.signal(signal.SIGTERM, on_exit)
