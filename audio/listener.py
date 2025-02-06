import re
from typing import Tuple
import speech_recognition as sr
import pyttsx3
from word2number import w2n


# Initialize the pyttsx3 engine for text-to-speech
engine = pyttsx3.init()

# have speaker ask for first coordinate, then detect for second one
# needs to recognize words, roman numerals, and time
# alpha bravo charlie delta echo foxtrot golf hotel
# for not 4!!!


def get_coordinate_input(timeout: float = 10) -> Tuple[str, str]:
    # Obtain audio from the microphone
    recognized = get_single_input()
    print("before", recognized)

    # recognizes a word, space and a letter and digit

    new_recognized = ''
    for word in recognized.split():
        try:
            new_recognized += str(w2n.word_to_num(word)) + " "
        except:
            new_recognized += word + " "

    print("recognized:", new_recognized)
    from_coord, to_coord = re.findall(r"[a-zA-Z]+\s?\d", new_recognized)[:2]

    print("from", from_coord, to_coord)
    from_coord = from_coord[0] + from_coord[-1]
    to_coord = to_coord[0] + to_coord[-1]
    print("after", from_coord, to_coord)

    speak_movement(from_coord, to_coord)

    return from_coord, to_coord


def get_single_input(timeout: float = 10) -> str:
    # Obtain audio from the microphone
    r = sr.Recognizer()
    r.pause_threshold = 1.3

    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source, timeout=timeout)
        r.adjust_for_ambient_noise(source)

    # Recognize speech using Google Speech Recognition
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


def speak_movement(from_coord: str, to_coord: str):
    # Speak the movement out loud
    movement_message = f"I am moving from {from_coord} to {to_coord}"
    engine.setProperty('rate', 150)
    voices = engine.getProperty("voices")
    for i in range(10):
        engine.setProperty('voice', voices[i].id)
        engine.say(movement_message)
    # Wait until the speech is finished
    engine.runAndWait()


if __name__ == "__main__":
    # Get coordinates and announce the movement
    get_coordinate_input()
