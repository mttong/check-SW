#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import time
import logging
import subprocess
import spidev as SPI
from PIL import Image, ImageDraw, ImageFont

sys.path.append("..")
from lib import LCD_2inch
# from LCD_Module_RPI_code.RaspberryPi.python.lib import LCD_2inch


class LCD:
    def __init__(self):
        # Raspberry Pi pin configuration for LCD1 and LCD2
        self.BL1, self.RST1, self.DC1, self.CS1 = 18, 27, 25, 8
        self.BL2, self.RST2, self.DC2, self.CS2 = 23, 6, 12, 7

        # SPI bus settings
        self.bus = 0

        logging.basicConfig(level=logging.DEBUG)

        # Initialize LCDs
        self.disp1 = LCD_2inch.LCD_2inch(spi=SPI.SpiDev(self.bus, 0), spi_freq=10000000, rst=self.RST1, dc=self.DC1, bl=self.BL1)
        self.disp2 = LCD_2inch.LCD_2inch(spi=SPI.SpiDev(self.bus, 1), spi_freq=10000000, rst=self.RST2, dc=self.DC2, bl=self.BL2)

        self._init_displays()

        # Load font
        self.font = ImageFont.truetype("/home/chess/Desktop/sw/check-SW-origin-audio-test/LCD_Module_RPI_code/RaspberryPi/python/Font/Font00.ttf", 40)
        #self.font = ImageFont.truetype("../Font/Font00.ttf", 40)
        self.font2 = ImageFont.truetype("/home/chess/Desktop/sw/check-SW-origin-audio-test/LCD_Module_RPI_code/RaspberryPi/python/Font/Font00.ttf", 30)

    def _init_displays(self):
        """Initialize and clear both LCDs."""
        for disp in [self.disp1, self.disp2]:
            disp.Init()
            disp.clear()
            disp.bl_DutyCycle(100)

    def display_ip_address(self):
        """Display the device's IP address on both screens."""
        ip_addr = subprocess.getoutput("hostname -I").strip()
        image = Image.new("RGB", (self.disp1.height, self.disp1.width), "WHITE")
        draw = ImageDraw.Draw(image)
        draw.text((20, 5), ip_addr, fill="BLACK", font=self.font)

        self._show_image(image)

    def _show_image(self, image):
        """Show the same image on both LCDs."""
        self.disp1.ShowImage(image)
        self.disp2.ShowImage(image)

    def display_turn(self, player="Black", duration=5):
        """Display whose turn it is with a countdown timer."""
        background = Image.open("/home/chess/Downloads/background4.jpeg").resize((self.disp1.height, self.disp1.width))
        start_time = time.time()

        while True:
            elapsed_time = int(time.time() - start_time)
            minutes, seconds = divmod(elapsed_time, 60)
            time_str = f"{minutes:02}:{seconds:02}"

            if seconds > duration:
                break

            image = background.copy()
            draw = ImageDraw.Draw(image)
            draw.text((45, 5), f"{player}'s Turn", fill="BLACK", font=self.font)
            #draw.text((150, 100), time_str, fill="BLACK", font=self.font)
            draw.text((130, 70), "Speak into", fill="BLACK", font=self.font2)
            draw.text((150, 110), "the mic!", fill="BLACK", font=self.font2)
            
            self._show_image(image.rotate(180))
            time.sleep(1)

    def display_move(self, start, end):
        """Display the move made and show an image of the black king."""
        
        background = Image.open("/home/chess/Downloads/checkered.jpg").resize((self.disp1.height, self.disp1.width))
        
        image = background.copy()
        draw = ImageDraw.Draw(image)
        #image = Image.new("RGB", (self.disp1.height, self.disp1.width), "WHITE")
        #draw = ImageDraw.Draw(image)
        #draw.text((5, 10), f"Moved {start} to {end}", fill="BLACK", font=self.font)
        
        self._show_image(image)

        #black_king = Image.open('/home/chess/Downloads/BlackKing.jpeg')
        #self._show_image(black_king)

    def display_image(self, image_path):
        """Display a custom image on both LCDs."""
        image = Image.open(image_path).rotate(180)
        self._show_image(image)

    def run(self):
        """Main execution function."""
        try:
            self.display_ip_address()
            self.display_turn("Black", 5)
            while True:
                self.display_move("A1", "A3")
        except IOError as e:
            logging.error(e)
        except KeyboardInterrupt:
            self.cleanup()

    def cleanup(self):
        """Exit safely."""
        self.disp1.module_exit()
        self.disp2.module_exit()
        logging.info("Exiting...")


if __name__ == "__main__":
    chess_display = LCD()
    chess_display.run()

