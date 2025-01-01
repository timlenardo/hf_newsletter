#!/bin/bash

# Stop and disable the service
systemctl stop hf-newsletter.timer
systemctl disable hf-newsletter.timer
systemctl stop hf-newsletter.service

# Remove systemd files
rm /etc/systemd/system/hf-newsletter.service
rm /etc/systemd/system/hf-newsletter.timer

# Reload systemd daemon
systemctl daemon-reload

# Remove installation directory
rm -rf /opt/hf-newsletter

echo "Uninstallation complete."