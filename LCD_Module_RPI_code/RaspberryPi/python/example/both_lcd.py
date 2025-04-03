#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import os
import sys
import time
import logging
import subprocess
import spidev as SPI
sys.path.append("..")
from lib import LCD_2inch
from PIL import Image, ImageDraw, ImageFont, ImageSequence


# Raspberry Pi pin configuration for LCD1 and LCD2:
# Pin mappings for first LCD screen (LCD1)
BL1 = 18  # Backlight for the first LCD screen

RST1 = 27
DC1 = 25
CS1 = 8  # Chip select for LCD1

# Pin mappings for second LCD screen (LCD2)
BL2 = 23  
RST2 = 6
DC2 = 12
CS2 = 7  # Chip select for LCD2

# SPI bus and device settings
bus = 0 
device = 0 

logging.basicConfig(level=logging.DEBUG)

try:
    # Initialize first LCD screen (LCD1)
    disp1 = LCD_2inch.LCD_2inch(spi=SPI.SpiDev(bus, 0),spi_freq=10000000,rst=RST1,dc=DC1,bl=BL1)
    disp1.Init()
    disp1.clear()
    disp1.bl_DutyCycle(100)  

    # Initialize second LCD screen (LCD2)
    disp2 = LCD_2inch.LCD_2inch(spi=SPI.SpiDev(bus, 1),spi_freq=10000000,rst=RST2,dc=DC2,bl=BL2)
    disp2.Init()
    disp2.clear()
    disp2.bl_DutyCycle(100)  
    
    Font1 = ImageFont.truetype("../Font/Font00.ttf", 40)
    ip_addr = subprocess.getoutput("hostname -I").strip()
    
    image5 = Image.new("RGB", (disp1.height, disp1.width), "WHITE")
    draw = ImageDraw.Draw(image5)
    i = 0
    while i < 1:
        draw.text((20, 5), ip_addr, fill="BLACK", font=Font1)
        i += 1
        time.sleep(1)
        disp1.ShowImage(image5)
        disp2.ShowImage(image5)

    # Image 1 = Black's turn!
    image1 = Image.new("RGB", (disp1.height, disp1.width), "WHITE")
    draw = ImageDraw.Draw(image1)
    
    background_image = Image.open("/home/chess/Downloads/background4.jpeg") 

    # Resize to match LCD dimensions
    background_image = background_image.resize((disp1.height, disp1.width))
    
    start_time = time.time()

    while True:  # Continuous loop to update timer
        elapsed_time = int(time.time() - start_time)  # Calculate elapsed seconds
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_str = f"{minutes:02}:{seconds:02}"  # Format as MM:SS
        
        if seconds > 5:
            break
        
        image = background_image.copy()
        draw = ImageDraw.Draw(image)

        # Create new image
        #image = Image.new("RGB", (disp1.height, disp1.width), "WHITE")
        #draw = ImageDraw.Draw(image)

        draw.text((45, 5), "Black's Turn", fill="BLACK", font=Font1)
        draw.text((150, 100), time_str, fill="BLACK", font=Font1)

        image = image.rotate(180)  # Rotate for LCD orientation

        # Display on both screens
        disp1.ShowImage(image)
        disp2.ShowImage(image)

        time.sleep(1)  # Wait for 1 second before updating

    
    # Image 2 = White's turn!
    
    # Image 3 = After Black's move is made
    
    # Confirm move
    image6 = Image.new("RGB", (disp1.height, disp1.width), "WHITE")
    draw = ImageDraw.Draw(image5)
    i = 0
    while i < 5:
        draw.text((20, 5), "Confirm A1 to A3?", fill="BLACK", font=Font1)
        i += 1
        time.sleep(1)
        disp1.ShowImage(image6)
        disp2.ShowImage(image6)
    
    
    while True:
        image3 = Image.new("RGB", (disp1.height, disp1.width), "WHITE")
        
        draw.text((5, 10), "Moved A1 to A3", fill="WHITE", font=Font1)
        
        black_king = Image.open('/home/chess/Downloads/BlackKing.jpeg')
        disp1.ShowImage(black_king)
        disp2.ShowImage(black_king)
        
    

    # Load an external image (you can modify the path as needed)
    image = Image.open('/home/chess/Downloads/shafai.jpeg')
    image2 = Image.open('/home/chess/Downloads/thomas.jpeg')
    image = image.rotate(180)
    #disp1.ShowImage(image)
    #disp2.ShowImage(image2)

    # Display the image continuously on both LCDs
    #while True:
    #    disp1.ShowImage(image)  # Show the image on LCD1
    #    disp2.ShowImage(image2)  # Show the image on LCD2
    #    time.sleep(1)

except IOError as e:
    logging.info(e)
except KeyboardInterrupt:
    disp1.module_exit()
    disp2.module_exit()
    logging.info("quit:")
    exit()
