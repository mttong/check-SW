#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys 
import time
import logging
import spidev as SPI
import RPi.GPIO as GPIO  # To control GPIO pins for chip select
sys.path.append("..")
from lib import LCD_2inch
from PIL import Image, ImageDraw, ImageFont

# Raspberry Pi pin configuration:
# Pin mappings for first LCD screen (LCD1)
BL1 = 18
RST1 = 27
DC1 = 25
CS1 = 8  # Chip select for LCD1

# Pin mappings for second LCD screen (LCD2)
BL2 = 23
RST2 = 27
DC2 = 12
CS2 = 7  # Chip select for LCD2

# SPI bus and device settings
bus = 0 
device = 0 

logging.basicConfig(level=logging.DEBUG)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(CS1, GPIO.OUT)
GPIO.setup(CS2, GPIO.OUT)
GPIO.output(CS1, GPIO.HIGH)  # Start with both chip selects high (inactive)
GPIO.output(CS2, GPIO.HIGH)

try:
    # Initialize SPI interface
    spi = SPI.SpiDev(bus, device)
    spi.max_speed_hz = 10000000  # Set the SPI frequency

    # Initialize first LCD screen (LCD1)
    disp1 = LCD_2inch.LCD_2inch(spi=spi, rst=RST1, dc=DC1, bl=BL1)  # No 'cs' argument
    disp1.Init()
    disp1.clear()
    disp1.bl_DutyCycle(50)  # Set backlight for LCD1 to 50%

    # Initialize second LCD screen (LCD2)
    disp2 = LCD_2inch.LCD_2inch(spi=spi, rst=RST1, dc=DC2, bl=BL2)  # No 'cs' argument
    disp2.Init()
    disp2.clear()
    disp2.bl_DutyCycle(50)  # Set backlight for LCD2 to 50%

    # Create blank image for drawing
    image1 = Image.new("RGB", (disp1.height, disp1.width), "WHITE")
    draw = ImageDraw.Draw(image1)

    # Draw shapes, text, and other elements for LCD1
    draw.rectangle((5, 10, 6, 11), fill="BLACK")
    draw.rectangle((5, 25, 7, 27), fill="BLACK")
    draw.rectangle((5, 40, 8, 43), fill="BLACK")
    draw.rectangle((5, 55, 9, 59), fill="BLACK")

    # Add lines, rectangles, and text to the image for LCD1
    draw.line([(20, 10), (70, 60)], fill="RED", width=1)
    draw.line([(70, 10), (20, 60)], fill="RED", width=1)
    draw.line([(170, 15), (170, 55)], fill="RED", width=1)
    draw.line([(150, 35), (190, 35)], fill="RED", width=1)

    # Draw other shapes and text for LCD1
    Font1 = ImageFont.truetype("../Font/Font01.ttf", 25)
    Font2 = ImageFont.truetype("../Font/Font01.ttf", 35)
    Font3 = ImageFont.truetype("../Font/Font02.ttf", 32)
    draw.text((5, 68), 'Hello world', fill="BLACK", font=Font1)
    draw.text((5, 118), 'WaveShare', fill="WHITE", font=Font2)
    draw.text((5, 160), '1234567890', fill="GREEN", font=Font3)

    image1 = image1.rotate(180)

    # Show image on first display (LCD1)
    GPIO.output(CS1, GPIO.LOW)  # Select LCD1 (set CS1 LOW)
    disp1.ShowImage(image1)
    GPIO.output(CS1, GPIO.HIGH)  # Deselect LCD1 (set CS1 HIGH)

    # Add a small delay before showing on the second display
    time.sleep(0.5)

    # Show image on second display (LCD2)
    GPIO.output(CS2, GPIO.LOW)  # Select LCD2 (set CS2 LOW)
    disp2.ShowImage(image1)
    GPIO.output(CS2, GPIO.HIGH)  # Deselect LCD2 (set CS2 HIGH)

    # Sleep to show image for a while
    time.sleep(3)

    logging.info("show image")

    # Load an external image (you can modify the path as needed)
    image = Image.open('/home/chess/Downloads/chess_pic.jpeg')
    image = image.rotate(180)

    # Display the image continuously on both LCDs
    while True:
        GPIO.output(CS1, GPIO.LOW)  # Select LCD1 (set CS1 LOW)
        disp1.ShowImage(image)
        GPIO.output(CS1, GPIO.HIGH)  # Deselect LCD1 (set CS1 HIGH)

        time.sleep(0.5)  # Small delay to prevent simultaneous updates and glitches

        GPIO.output(CS2, GPIO.LOW)  # Select LCD2 (set CS2 LOW)
        disp2.ShowImage(image)
        GPIO.output(CS2, GPIO.HIGH)  # Deselect LCD2 (set CS2 HIGH)

        time.sleep(1)

except IOError as e:
    logging.info(e)
except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO on program exit
    disp1.module_exit()
    disp2.module_exit()
    logging.info("quit:")
    exit()
