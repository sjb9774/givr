from givr.app import app
from givr.views import *
from givr.endpoints import *
import argparse
import threading

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--daemon", action="store_true", default=False)

    args = parser.parse_args()

    if args.daemon:
        t = threading.Thread(target=app.run, args=(), kwargs={})
        t.start()
    else:
        app.run(debug=True)
