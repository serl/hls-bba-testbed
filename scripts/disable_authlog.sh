#!/usr/bin/env bash

conf_file='/etc/rsyslog.d/50-default.conf'
backup_file='/home/vagrant/50-default.conf_backup'

cp "$conf_file" "$backup_file"
grep --invert-match 'auth' "$backup_file" > "$conf_file"

echo 'auth,authpriv.* /dev/null' >> "$conf_file"
echo '*.*;auth,authpriv.none -/dev/null' >> "$conf_file"

reload rsyslog
service rsyslog restart
rm /var/log/auth.log*

