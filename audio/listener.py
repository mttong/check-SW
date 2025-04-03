import re
from typing import Tuple
import speech_recognition as sr
import pyttsx3
from word2number import w2n
import serial
import time

# have speaker ask for first coordinate, then detect for second one
# needs to recognize words, roman numerals, and time
# alpha bravo charlie delta echo foxtrot golf hotel
# for not 4!!!

# add a function to listen to the start of the game


class Listener:
    def __init__(self):
        # Initialize the pyttsx3 engine for text-to-speech
        self.engine = pyttsx3.init()

    def get_coordinate_input(self, timeout: float = 10) -> Tuple[str, str]:
        """Obtain coordinates from speech input and announce the movement."""

        while True:
            recognized = self.get_single_input(timeout)

            print("before", recognized)

            # Process the recognized speech and convert number words to digits
            new_recognized = ''
            for word in recognized.split():
                try:
                    new_recognized += str(w2n.word_to_num(word)) + " "
                except:
                    new_recognized += word + " "

            print("recognized:", new_recognized)

            # Extract coordinates using regex (e.g., A1, B2, etc.)
            coords = re.findall(r"[a-zA-Z]+\s?\d", new_recognized)

            if not len(coords) < 2:
                break

        from_coord, to_coord = coords[:2]

        print("from", from_coord, to_coord)

        from_coord = from_coord[0] + from_coord[-1]
        to_coord = to_coord[0] + to_coord[-1]
        print("after", from_coord, to_coord)

        self.speak_movement(from_coord, to_coord)

        return from_coord, to_coord

    def get_single_input(self, timeout: float = 10) -> str:
        """Capture audio from the microphone and recognize speech."""
        r = sr.Recognizer()

        r.pause_threshold = 1.3

        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source, timeout=timeout)
            r.adjust_for_ambient_noise(source)

        try:
            recognized = r.recognize_google(audio)
            print("Google Speech Recognition thinks you said: " + recognized)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            recognized = ""
        except sr.RequestError as e:
            print(
                f"Could not request results from Google Speech Recognition service; {e}")
            recognized = ""

        return recognized

    def speak_movement(self, from_coord: str, to_coord: str):
        # Speak the movement out loud
        movement_message = f"I am moving from {from_coord} to {to_coord}"
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0) 
        voices = self.engine.getProperty("voices")
        self.engine.setProperty('voice', voices[24].id)
        self.engine.say(movement_message)
        # Wait until the speech is finished
        self.engine.runAndWait()


if __name__ == "__main__":
    # Create a Game instance and start the game
    listener = Listener()
    listener.get_coordinate_input()
