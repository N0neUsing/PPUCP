# -*- coding: utf-8 -*-
import sys

from zk import ZK, const

sys.path.append("zk")

conn = None
zk = ZK('192.168.16.99', port=4370, timeout=5)
try:
    print ('Connecting to device ...')
    conn = zk.connect()
    conn.enroll_user()

except Exception as e:
    print ("Process terminate : {}".format(e))
finally:
    if conn:
        conn.disconnect()
