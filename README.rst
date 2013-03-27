==================================
 Tuyau: personal information pipe
==================================

Tuyau would like to do for email (and RSS, and contacts, and
calendaring) what git does for source code (and personal config files,
and org files, and bugs). That is: make sharing easy, transparent,
disconnected, and reliable.

Of course, right now it's more of a proof-of-concept, a kind of
offline message bus. You put a message on the bus, and the nodes that are interested in that message eventually get it.

Each node in the graph has a set of remotes, where it looks for
messages. It also has a bunch of listeners. Listeners control what
messages it's interested in, and what to do with them. Among other
things, "what to do" can mean sending other messages.

Tuyau is implemented as a layer over CouchDB. Eventually, all data
should be in CouchDB and applications should be taught to use Couch as
a backend, but in the meantime, we can use Tuyau to bootstrap
up. Store data in Couch, and use Tuyau to feed applications running
locally.

Tuyau is French for "pipe" (not the kind you smoke out of, but a
tube).

Install
=======

Tuyau would like you to have the following Python modules installed:

- paramiko
- json

Development
===========

By default, the unit tests run against localhost, so make sure you
have an authorized key for your own account on localhost.

Paramiko doesn't completely support ECDSA keys yet (see `issue 88
<https://github.com/paramiko/paramiko/issues/88>`_), so you might need
to disable serving ECDSA in SSHD, then reconnect with openssh's client
and accept the RSA key. I'm working on it, I promise.

Then, run ``py.test`` to run the tests.
