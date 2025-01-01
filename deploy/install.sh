#!/bin/bash

# Make script executable
chmod +x "$(dirname "$0")/install.sh"

# Create necessary directories
mkdir -p /opt/hf-newsletter
mkdir -p /opt/hf-newsletter/logs
mkdir -p /opt/hf-newsletter/data

# Copy files to installation directory
cp -r ../src /opt/hf-newsletter/
cp -r ../requirements.txt /opt/hf-newsletter/
cp ../.env /opt/hf-newsletter/

# Install Python requirements
pip install -r /opt/hf-newsletter/requirements.txt

# Copy systemd service files
cp hf-newsletter.service /etc/systemd/system/
cp hf-newsletter.timer /etc/systemd/system/

# Reload systemd daemon
systemctl daemon-reload

# Enable and start the timer
systemctl enable hf-newsletter.timer
systemctl start hf-newsletter.timer

echo "Installation complete. Service will run daily at 9 AM."
echo "To check status: systemctl status hf-newsletter.timer"
echo "To check next run: systemctl list-timers hf-newsletter.timer"
echo "To check logs: tail -f /opt/hf-newsletter/logs/service.log"