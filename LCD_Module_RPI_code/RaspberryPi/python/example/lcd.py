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
#from LCD_Module_RPI_code.RaspberryPi.python.lib import LCD_2inch


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
        self.font = ImageFont.truetype("/home/chess/Desktop/sw/check-SW-origin-audio-test/LCD_Module_RPI_code/RaspberryPi/python/Font/Font02.ttf", 40)
        #self.font = ImageFont.truetype("../Font/Font00.ttf", 40)
        self.font2 = ImageFont.truetype("/home/chess/Desktop/sw/check-SW-origin-audio-test/LCD_Module_RPI_code/RaspberryPi/python/Font/Font00.ttf", 30)
        self.font3 = ImageFont.truetype("/home/chess/Desktop/sw/check-SW-origin-audio-test/LCD_Module_RPI_code/RaspberryPi/python/Font/Font00.ttf", 25)

    def _init_displays(self):
        """Initialize and clear both LCDs."""
        for disp in [self.disp1, self.disp2]:
            disp.Init()
            disp.clear()
            disp.bl_DutyCycle(100)
            
    def display_default_images(self):
        background1 = Image.open("/home/chess/Downloads/background4.jpeg").resize((self.disp1.height, self.disp1.width))
        image1 = background1.copy()
        
        background2 = Image.open("/home/chess/Downloads/background4.jpeg").resize((self.disp2.height, self.disp2.width))
        image2 = background2.copy()
        
        self.disp1.ShowImage(image1)
        self.disp2.ShowImage(image2)

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

    def display_turn_black(self, duration=5):
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
            draw.text((45, 5), "Black's Turn", fill="BLACK", font=self.font)
            draw.text((130, 70), "Speak into", fill="BLACK", font=self.font2)
            draw.text((130, 110), "the mic!", fill="BLACK", font=self.font2)
            
            self._show_image(image.rotate(180))
            time.sleep(1)
            
    def display_turn_white(self, duration=5):
        """Display whose turn it is with a countdown timer."""
        background = Image.open("/home/chess/Downloads/white_piece.png").resize((self.disp1.height, self.disp1.width))
        start_time = time.time()

        while True:
            elapsed_time = int(time.time() - start_time)
            minutes, seconds = divmod(elapsed_time, 60)
            time_str = f"{minutes:02}:{seconds:02}"

            if seconds > duration:
                break

            image = background.copy()
            draw = ImageDraw.Draw(image)
            draw.text((45, 5), "White's Turn", fill="BLACK", font=self.font)
            draw.text((50, 70), "Speak into", fill="BLACK", font=self.font2)
            draw.text((50, 110), "the mic!", fill="BLACK", font=self.font2)
            
            self._show_image(image.rotate(180))
            time.sleep(1)

    def display_move(self, start, end):
        background = Image.open("/home/chess/Downloads/move_piece.png").resize((self.disp1.height, self.disp1.width))
        #background2 = Image.open("/home/chess/Downloads/checkered.jpg").resize((self.disp1.height * 2 // 3, self.disp1.width))
        
        image = background.copy()
        draw = ImageDraw.Draw(image)
        #image = Image.new("RGB", (self.disp1.height, self.disp1.width), "WHITE")
        #draw = ImageDraw.Draw(image)
        
        #image = Image.new("RGB", (self.disp1.height, self.disp1.width), "WHITE")
        #draw = ImageDraw.Draw(image)
        draw.text((95, 20), f"Moved", fill="BLACK", font=self.font2)
        draw.text((125, 60), f"{start}", fill="BLUE", font=self.font2)
        draw.text((135, 100), f"to", fill="BLACK", font=self.font2)
        draw.text((125, 140), f"{end}", fill="BLUE", font=self.font2)

        #black_king = Image.open('/home/chess/Downloads/BlackKing.jpeg')
        #self._show_image(black_king)
        #image.paste(background, (0, self.disp1.width // 2))
        #image.paste(background, (self.disp1.height * 2 // 3, self.disp1.width))
        
        self._show_image(image)
        
    def try_again(self):
        """Display a custom image on both LCDs."""
        background = Image.open("/home/chess/Downloads/background6.png").resize((self.disp1.height, self.disp1.width))
        image = background.copy()
        draw = ImageDraw.Draw(image)
        
        draw.text((25, 5), "Move not recognized", fill="RED", font=self.font)
        draw.text((80, 60), "Try again!", fill="BLACK", font=self.font)
        
        self._show_image(image)
        
    def invalid_move(self):
        """Display a custom image on both LCDs."""
        background = Image.open("/home/chess/Downloads/invalid.png").resize((self.disp1.height, self.disp1.width))
        image = background.copy()
        draw = ImageDraw.Draw(image)
        
        #draw.text((60, 5), "Invalid move", fill="BLACK", font=self.font2)
        draw.text((20, 0), "Invalid move. Try again!", fill="BLACK", font=self.font3)
        
        self._show_image(image)

    def display_image(self, image_path, text = ""):
        """Display a custom image on both LCDs."""
        background = Image.open(image_path).resize((self.disp1.height, self.disp1.width))
        image = background.copy()
        draw = ImageDraw.Draw(image)
        
        draw.text((20, 20), text, fill="RED", font=self.font)
        
        self._show_image(image)
        
    def display_image2(self, image_path, text = ""):
        """Display a custom image on both LCDs."""
        background = Image.open(image_path).resize((self.disp1.width, self.disp1.height))
        image = background.copy()
        draw = ImageDraw.Draw(image)
        
        draw.text((20, 20), text, fill="RED", font=self.font)
        
        self._show_image(image)
        
    def motor_calibrating(self):
        background = Image.open("/home/chess/Downloads/gear.jpg")
        background = background.resize((self.disp1.height, self.disp1.width // 2))

        # Create a new image for the full screen (white background)
        full_image = Image.new("RGB", (self.disp1.height, self.disp1.width), "WHITE")

        # Draw the text on the top half of the full image
        draw = ImageDraw.Draw(full_image)
        draw.text((95, 10), "Motor", fill="BLACK", font=self.font)
        draw.text((45, 60), "Calibrating!", fill="BLACK", font=self.font)

        full_image.paste(background, (0, self.disp1.width // 2))
        self._show_image(full_image)
        
    def run(self):
        """Main execution function."""
        try:
            self.display_ip_address()
            self.display_turn_black(2)
            self.display_turn_white(2)
            
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
    #while True:
    #for i in range(0,3):
    #    chess_display.display_image("/home/chess/Downloads/wolf.jpg", "READY TO PLAY???")
    #for i in range(0,3):
    #    chess_display.display_image2("/home/chess/Downloads/wolf2.jpg")
    #for i in range(0,3):
    #    chess_display.display_image2("/home/chess/Downloads/wolf3.jpg")
    for i in range(0,5):
        chess_display.try_again()
    for i in range(0,5):
        chess_display.invalid_move()
    chess_display.motor_calibrating()
    chess_display.run()
