# raspiUPS

Waveshare CM4-POE-UPS (C) control service for Raspberry Pi 

It permanently checks the battery and shuts the Raspberry down if the battery gets empty.

This is a fork of https://github.com/vonKloppen/raspiUPS with some changes and extensions

 + Use the Waveshare POE-UPS Board with an Raspberry Pi Compute Module 4
 + Install script added
 + Send data to openHAB

## Battery control code

You find the source code in the bin directory, you can decide between two variants

 + raspiUPS-hatC.py
   Original code, from Kloppen, use log file, but i2c adapted for POE-UPS board
 + raspiUPS-hatC-openHAB.py
   Adopted code, i2c adapted for POE-UPS board and openHAB instead of log file

## Battery control service

Use the install.sh script to install the deamon, the script must be run as root i.e. sudo ./install.sh

Have a look in the script decide between the code using log files (like Kloppen) or openHAB communication.

## OpenHAB integration

I use an old openHAB version 2 installation, but it should work with newer versions too. See https://www.openhab.org

You find my item definition in openHAB/raspiUPS.items

The communication is done via the REST interface. In my code there is no access control included. In newer openHAB version you might have to add you REST token to the post or get method.
