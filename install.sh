#!/bin/sh
# run as root in this directory to install the raspiUPS service

# Create Log directory, see raspiUPS-hatC.py code
mkdir /var/log/raspiUPS/
# Copy Python file to a good location and change permissions
# Original code, from Kloppen, use log file, but i2c adapted for POE-UPS board
cp bin/raspiUPS-hatC.py /usr/sbin/raspiUPS-hatC.py
# Adopted code, i2c adapted for POE-UPS board and openHAB instead of log file
#cp bin/raspiUPS-hatC-openHAB.py /usr/sbin/raspiUPS-hatC.py
chmod u+x /usr/sbin/raspiUPS-hatC.py
# Copy service file
cp systemd/raspiUPS.service /lib/systemd/system/
ln -s /lib/systemd/system/raspiUPS.service /etc/systemd/system/
# Reload services, this will find the new raspiUPS service
systemctl daemon-reload
# Enable and start the service
systemctl enable raspiUPS
systemctl start raspiUPS
# Check Status
systemctl status raspiUPS