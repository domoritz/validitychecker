#!/usr/bin/env python
# -*- coding: utf-8 -*-

#http://python-nose.googlecode.com/svn/trunk/nose/twistedtools.py

_twisted_thread = None

def threaded_reactor():
    """
    Start the Twisted reactor in a separate thread, if not already done.
    Returns the reactor.
    The thread will automatically be destroyed when all the tests are done.
    """
    global _twisted_thread
    try:
        from twisted.internet import reactor
    except ImportError:
        return None, None
    if not _twisted_thread:
        print "starting reactor"
        from twisted.python import threadable
        from threading import Thread
        _twisted_thread = Thread(target=lambda: reactor.run( \
                installSignalHandlers=False))
        _twisted_thread.setDaemon(True)
        _twisted_thread.start()
    return reactor, _twisted_thread

# Export global reactor variable, as Twisted does
reactor, reactor_thread = threaded_reactor()


def stop_reactor():
    """Stop the reactor and join the reactor thread until it stops.
    Call this function in teardown at the module or package level to
    reset the twisted system after your tests. You *must* do this if
    you mix tests using these tools and tests using twisted.trial.
    """
    global _twisted_thread
    reactor.stop()
    reactor_thread.join()
    _twisted_thread = None

if __name__ == '__main__':
    threaded_reactor()
    threaded_reactor()
    #stop_reactor()
