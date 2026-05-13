# Demo 1 — Flask on a Single EC2 Instance

A minimal Flask app served by Gunicorn under systemd on an EC2 instance.

> ⚠️ **AMI matters.** The user-data script is OS-specific. Use the version below that matches the AMI you launched.

## EC2 User Data — Ubuntu (22.04 / 24.04 / 26.04)

```bash
#!/bin/bash
# Runs once on first boot, as root
set -e

# Update the system and install Python + git
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip python3-venv git

# Clone the application repository
cd /home/ubuntu
git clone https://github.com/mangucletus/aws-python-deployment.git
chown -R ubuntu:ubuntu aws-python-deployment

# Install dependencies into a venv inside the demo1 folder
cd aws-python-deployment/main/demo1
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
chown -R ubuntu:ubuntu /home/ubuntu/aws-python-deployment

# Create the systemd unit file
cat > /etc/systemd/system/flaskapp.service <<EOF
[Unit]
Description=Flask App (Demo 1)
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/aws-python-deployment/main/demo1
ExecStart=/home/ubuntu/aws-python-deployment/main/demo1/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:80 app:app
AmbientCapabilities=CAP_NET_BIND_SERVICE
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start the service and enable it on boot
systemctl daemon-reload
systemctl enable flaskapp
systemctl start flaskapp
```

## EC2 User Data — Amazon Linux 2023

```bash
#!/bin/bash
set -e

dnf update -y
dnf install -y python3 python3-pip git

cd /home/ec2-user
git clone https://github.com/mangucletus/aws-python-deployment.git
chown -R ec2-user:ec2-user aws-python-deployment

cd aws-python-deployment/main/demo1
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
chown -R ec2-user:ec2-user /home/ec2-user/aws-python-deployment

cat > /etc/systemd/system/flaskapp.service <<EOF
[Unit]
Description=Flask App (Demo 1)
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/aws-python-deployment/main/demo1
ExecStart=/home/ec2-user/aws-python-deployment/main/demo1/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:80 app:app
AmbientCapabilities=CAP_NET_BIND_SERVICE
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable flaskapp
systemctl start flaskapp
```

## What Changed vs. The Original Script

| Issue | Before | After |
| --- | --- | --- |
| Clone dir name | `chown ... flask-app` | `chown ... aws-python-deployment` |
| App location | `cd flask-app` | `cd aws-python-deployment/main/demo1` |
| WorkingDirectory | `/home/ec2-user/flask-app` | `/home/ec2-user/aws-python-deployment/main/demo1` |
| ExecStart path | `/home/ec2-user/flask-app/venv/...` | `/home/ec2-user/aws-python-deployment/main/demo1/venv/...` |
| Port 80 as non-root | Would fail (`Permission denied`) | Added `AmbientCapabilities=CAP_NET_BIND_SERVICE` |
| Python version | `python3.12` (not in AL2023 default repos) | `python3` (AL2023 default) |

## Security Group

Allow inbound:
- **TCP 80** from `0.0.0.0/0` (HTTP)
- **TCP 22** from your IP (SSH)

## Verifying

After the instance boots (give it ~2 minutes), visit:

```
http://<EC2_PUBLIC_IP>/
http://<EC2_PUBLIC_IP>/health
```

If something looks wrong, SSH in and check:

```bash
sudo systemctl status flaskapp
sudo journalctl -u flaskapp -n 50 --no-pager
sudo cat /var/log/cloud-init-output.log
```

---

> **Next:** for the ALB + Auto Scaling Group setup (and how to stress-test that scaling works), see [../demo2/README.md](../demo2/README.md).
