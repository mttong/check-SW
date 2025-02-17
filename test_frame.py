from picamera2 import Picamera2
#from libcamera import controls
import cv2
import time
import pupil_apriltags as apriltag
#import apriltag

camera = Picamera2()

config = camera.create_still_configuration(raw={}, display=None)
camera.configure(config)

camera.start()
time.sleep(2)
camera.capture_file("/home/chess/Documents/check-SW/image.jpg")
img = cv2.imread("/home/chess/Documents/check-SW/image.jpg")

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

detector = apriltag.Detector(families="tag36h11")
results = detector.detect(gray)

print(results)

print("Done.")
camera.close()
