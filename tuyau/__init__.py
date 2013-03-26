"""
Tuyau: a flexible pipe for personal information

"""

# Try to use paramiko in the local directory.
# This is to help develop paramiko.
import sys
import os.path
try:
    import paramiko
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'paramiko'))
    import paramiko
