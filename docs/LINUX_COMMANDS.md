# Linux Practice

```bash
pwd
ls -la
cd /path
mkdir demo
touch file.txt
chmod 755 script.sh
chown user:group file.txt
whoami
id
ps aux
systemctl status nginx
ip addr
ss -tulpn
ping 8.8.8.8
curl http://localhost:5000/health
journalctl -u nginx
tail -f /var/log/syslog
```

Basic shell:
```bash
#!/bin/bash
set -e
curl -fsS http://localhost:5000/health
echo "Healthy"
```
