import re
from typing import Tuple
import speech_recognition as sr


def get_coordinate_input(timeout: float = 10) -> Tuple[str, str]:
    # obtain audio from the microphone
    recognized = get_single_input()

    from_coord, to_coord = re.findall(r"[a-zA-Z]\d", recognized)[:2]

    return from_coord, to_coord

def get_single_input(timeout: float = 10) -> str:
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source, timeout=timeout)

    # recognize speech using Google Speech Recognition
    try:
        print("Google Speech Recognition thinks you said " + (recognized := r.recognize_google(audio)))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

    return recognized


if __name__ == "__main__":
    get_coordinate_input()