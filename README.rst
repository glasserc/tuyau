==================================
 Tuyau: personal information pipe
==================================

Tuyau would like to do for email (and RSS, and contacts, and
calendaring) what git does for source code (and personal config files,
and org files, and bugs). That is: make sharing easy transparent,
disconnected, and reliable.

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
