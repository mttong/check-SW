from picamera2 import Picamera2
#from libcamera import controls
import cv2
import time
import pupil_apriltags as apriltag
import numpy as np
#import apriltag


CHESS_PIECES = {
	'black_pawn': 2,
	'black_rook': 4,
	'black_bishop': 6,
	'black_knight': 8,
	'black_queen': 10,
	'black_king': 12
}

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
	return results
	
def calibrate_board_left(results):
	left_boundary_x = np.array([])
	left_boundary_y = np.array([])
	for tag in results:
		#check if tag is black
		if tag.tag_id % 2 == 0 and tag.tag_id != 2:
			min_corner_x = 2048.0
			min_corner = []
			for corner in tag.corners:
				if corner[0] < min_corner_x:
					min_corner_x = corner[0]
					min_corner = corner
			left_boundary_x = np.append(left_boundary_x, min_corner_x)
			left_boundary_y = np.append(left_boundary_y, min_corner[1])
			print(f"Tag: {tag.tag_id}, Left Most Corner: {min_corner}")
			
	m, b = np.polyfit(left_boundary_x,left_boundary_y,1)
	
	img = cv2.imread("/home/chess/Documents/check-SW/image.jpg")
	num_pixels_y = img.shape[1]
	
	x1, y1 = 0, int(b)
	x2, y2 = num_pixels_y, int(m * num_pixels_y + b)
	cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0) ,5)
	for i in range(len(left_boundary_x)):
		cv2.circle(img, (int(left_boundary_x[i]), int(left_boundary_y[i])), 10, (0, 0, 255), -1)
	
	cv2.imwrite("/home/chess/Documents/check-SW/image.jpg", img)
	
	
if __name__ == "__main__":
	camera = Picamera2()

	config = camera.create_still_configuration(raw={}, display=None)
	camera.configure(config)
	
	camera.set_controls({"ExposureTime": 50000, "AnalogueGain": 1.0})

	camera.start()
	
	final_apriltag_results = []
	num_tags = 0
	for i in range(1):
		img = take_image(camera)
		results = detect_apriltags(img)
		print(len(results))
		if len(results) > num_tags:
			num_tags = len(results)
			final_apriltag_results = results
			
	print(f"Number Tags: {num_tags}")
	for tag in final_apriltag_results:
		print(f"April Tag ID: {tag.tag_id}, Center: {tag.center}, Corners: {tag.corners}")	
	
	calibrate_board_left(final_apriltag_results)
	
	camera.close()
