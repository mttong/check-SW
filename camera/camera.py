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
	
def detect_apriltags(img, brightness = 0.75):
	
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	gray = (gray*brightness).astype(np.uint8)

	detector = apriltag.Detector(families="tag36h11")
	results = detector.detect(gray)
	return results

def convert_line_eq_to_image_coords(m, b, img_height):
    # Convert slope (sign change due to y-axis flip)
	m_image = -m
    
    # Convert intercept (adjust for y-axis flip and origin shift)
	b_image = (img_height - b)
    
	return m_image, b_image
	
def return_col_min_max(min_corner_x_value, max_corner_x_value, tagcorners, 
						min_left_boundary_x, min_left_boundary_y, 
						max_left_boundary_x, max_left_boundary_y): 
							
	min_corner_x = min_corner_x_value
	min_corner = []
	max_corner_x = max_corner_x_value
	max_corner = []
			
	for corner in tagcorners:
		if corner[0] < min_corner_x:
			min_corner_x = corner[0]
			min_corner = corner
		if corner[0] > max_corner_x:
			max_corner_x = corner[0]
			max_corner = corner
				
	min_left_boundary_x = np.append(min_left_boundary_x, min_corner_x)
	min_left_boundary_y = np.append(min_left_boundary_y, min_corner[1])
	max_left_boundary_x = np.append(max_left_boundary_x, max_corner_x)
	max_left_boundary_y = np.append(max_left_boundary_y, max_corner[1])	
	
	return (min_left_boundary_x, min_left_boundary_y, 
			max_left_boundary_x, max_left_boundary_y)
    
def calibrate_board_columns(results, black_color = True):
	min_left_boundary_x = np.array([])
	min_left_boundary_y = np.array([])
	max_left_boundary_x = np.array([])
	max_left_boundary_y = np.array([])
	
	min_p_x = np.array([])
	min_p_y = np.array([])
	max_p_x = np.array([])
	max_p_y = np.array([])
	
	min_corner_x_value = 2592.0
	max_corner_x_value = 0.0
		
	pawn_tag_id = 2 if black_color else 3
	check_black = 0 if black_color else 1
	
	for tag in results:
		#check if tag is black
		if tag.tag_id % 2 == int(check_black) and tag.tag_id != pawn_tag_id:
			(min_left_boundary_x, min_left_boundary_y, 
			max_left_boundary_x, max_left_boundary_y) = return_col_min_max(min_corner_x_value, 
			max_corner_x_value, tag.corners, 
			min_left_boundary_x, min_left_boundary_y, 
			max_left_boundary_x, max_left_boundary_y)
			
		if tag.tag_id == pawn_tag_id:
			(min_p_x, min_p_y, 
			max_p_x, max_p_y) = return_col_min_max(min_corner_x_value, 
			max_corner_x_value, tag.corners, 
			min_p_x, min_p_y, 
			max_p_x, max_p_y)

    
	m_min, b_min = np.polyfit(min_left_boundary_x, min_left_boundary_y,1)
	m_max, b_max = np.polyfit(max_left_boundary_x, max_left_boundary_y,1)
	
	pawn_m_min, pawn_b_min = np.polyfit(min_p_x, min_p_y,1)
	pawn_m_max, pawn_b_max = np.polyfit(max_p_x, max_p_y,1)
	
	add_polyfit_lines(m_min, b_min, min_left_boundary_x, min_left_boundary_y)
	add_polyfit_lines(m_max, b_max, max_left_boundary_x, max_left_boundary_y)
	
	return pawn_m_min, pawn_b_min, pawn_m_max, pawn_b_max
			
def add_polyfit_lines(m, b, boundary_x, boundary_y):
				
	img = cv2.imread("/home/chess/Documents/check-SW/image.jpg")
	num_pixels_y = img.shape[1]
	
	x1, y1 = 0, int(b)
	x2, y2 = num_pixels_y, int(m * num_pixels_y + b)
	cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0) ,5)
	for i in range(len(boundary_x)):
		cv2.circle(img, (int(boundary_x[i]), int(boundary_y[i])), 10, (0, 0, 255), -1)
	
	cv2.imwrite("/home/chess/Documents/check-SW/image.jpg", img)
	
def add_polyfit_lines_col(m, b):
				
	img = cv2.imread("/home/chess/Documents/check-SW/image.jpg")
	num_pixels_y = img.shape[1]
	x1, y1 = 0, int(b)
	x2, y2 = num_pixels_y, int(m * num_pixels_y + b)
	cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0) ,5)
	
	cv2.imwrite("/home/chess/Documents/check-SW/image.jpg", img)
	
def avg_polyfit_line(m_max, b_max, m_min, b_min):
	#TODO: 2592 = image size, remove hard coded value
	y_values = np.arange(2592)
    
    # Calculate x-values for both lines at each y
	max_x = (y_values - b_max) / m_max
	min_x = (y_values - b_min) / m_min
    
    # Average the x-values at each y-coordinate
	avg_x = (max_x + min_x) / 2
    
    # Fit new line through (avg_x, y_values) points
	valid = np.isfinite(avg_x)
	m_avg, b_avg = np.polyfit(avg_x[valid], y_values[valid], 1)
	add_polyfit_lines_col(m_avg, b_avg)
	return m_avg, b_avg
	
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
	#for tag in final_apriltag_results:
	#	print(f"April Tag ID: {tag.tag_id}, Center: {tag.center}, Corners: {tag.corners}")	
	
	black = True
	white = False
	m_78, b_78, m_67, b_67 = calibrate_board_columns(final_apriltag_results, black)
	m_23, b_23, m_34, b_34 = calibrate_board_columns(final_apriltag_results, white)
	
	mid_p_m = (m_67 + m_23)/2
	mid_p_b = (b_67 + b_23)/2
	
	add_polyfit_lines_col(m_67, b_67)
	add_polyfit_lines_col(m_23, b_23)
	
	m_45, b_45 = avg_polyfit_line(m_67, b_67, m_23, b_23)
	m_56, b_56 = avg_polyfit_line(m_67, b_67, m_45, b_45)
	m_34, b_34 = avg_polyfit_line(m_45, b_45, m_23, b_23)

	
	camera.close()
