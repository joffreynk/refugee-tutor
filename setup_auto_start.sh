#!/bin/bash
# Camp Tutor Auto-Start Setup

# Create service file
echo '[Unit]
Description=Camp Tutor Robot
After=network.target

[Service]
Type=simple
User=refugee
WorkingDirectory=/home/refugee
ExecStart=/home/refugee/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target' | sudo tee /etc/systemd/system/camp_tutor.service

# Reload and enable
sudo systemctl daemon-reload
sudo systemctl enable camp_tutor
sudo systemctl start camp_tutor

# Set hostname
echo "refugee-tutor" | sudo tee /etc/hostname

# Update /etc/hosts
sudo sed -i 's/^127.0.1.*/127.0.1\trefugee-tutor/' /etc/hosts

echo "Done! Reboot with: sudo reboot"
echo "Access at: http://refugee-tutor.local:5000"