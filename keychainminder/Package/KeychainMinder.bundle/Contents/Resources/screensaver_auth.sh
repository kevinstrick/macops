#!/bin/sh
# 10/4/2013 by ks

# removes the last line of the /etc/pam.d/screensaver file, which allows for 
# unlocking the screensaver even if the account is an admin account using
# option+return at the lock screen
# works on 10.7.3+, 10.8.x, 10.9.x

cp /etc/pam.d/screensaver /etc/pam.d/screensaver.bak
grep -v "account    required       pam_group.so no_warn deny group=admin,wheel ruser fail_safe" /etc/pam.d/screensaver > /tmp/screensaver
mv /tmp/screensaver /etc/pam.d/
chown root:wheel /etc/pam.d/screensaver
chmod 644 /etc/pam.d/screensaver

exit 0




