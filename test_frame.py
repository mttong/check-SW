from picamera2 import Picamera2
#from libcamera import controls
import cv2
import time
import pupil_apriltags as apriltag
import numpy as np
#import apriltag



def take_image(camera):
	time.sleep(0.5)
	camera.capture_file("/home/chess/Documents/check-SW/image.jpg")
	img = cv2.imread("/home/chess/Documents/check-SW/image.jpg")
	return img
	
def detect_apriltags(img, brightness = 0.85):
	
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	gray = (gray*brightness).astype(np.uint8)

	detector = apriltag.Detector(families="tag36h11")
	results = detector.detect(gray)

	#print(f"Number of April Tags: {num_tags}")

	#for tag in results:
	#	print(f"April Tag ID: {tag.tag_id}, Center: {tag.center}")	
	return results
	
if __name__ == "__main__":
	camera = Picamera2()

	config = camera.create_still_configuration(raw={}, display=None)
	camera.configure(config)
	
	camera.set_controls({"ExposureTime": 50000, "AnalogueGain": 1.0})

	camera.start()
	
	final_apriltag_results = []
	num_tags = 0
	for i in range(5):
		img = take_image(camera)
		results = detect_apriltags(img)
		print(len(results))
		if len(results) > num_tags:
			num_tags = len(results)
			final_apriltag_results = results
			
	print(f"Number Tags: {num_tags}")
	for tag in final_apriltag_results:
		print(f"April Tag ID: {tag.tag_id}, Center: {tag.center}")	
	
	camera.close()
