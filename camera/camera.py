from picamera2 import Picamera2
#from libcamera import controls
import cv2
import time
import pupil_apriltags as apriltag
import numpy as np
#import apriltag

IMG_PATH = "/home/chess/Check/official-branch/camera/img.jpg"

CHESS_PIECES = {
	'black_pawn': 2,
	'black_rook': 4,
	'black_bishop': 6,
	'black_knight': 8,
	'black_queen': 10,
	'black_king': 12,
	'white_pawn': 3,
	'white_rook': 5,
	'white_bishop': 7,
	'white_knight': 9,
	'white_queen': 11,
	'white_king': 13
}

def take_image(camera):
	time.sleep(0.5)
	camera.capture_file(IMG_PATH)
	img = cv2.imread(IMG_PATH)
	return img
	
def detect_apriltags(img, brightness = 0.75):
	
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	gray = (gray*brightness).astype(np.uint8)

	detector = apriltag.Detector(families="tag36h11")
	results = detector.detect(gray)
	return results
	
	
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
    
def calibrate_col_bounds(results, black_color = True):
	min_boundary = [np.array([]), np.array([])]
	max_boundary = [np.array([]), np.array([])]
	min_pawn = [np.array([]), np.array([])]
	max_pawn = [np.array([]), np.array([])] 
	
	min_corner_x_value = 2592.0 #size of the image
	max_corner_x_value = 0.0
		
	pawn_tag_id = 2 if black_color else 3
	check_black = 0 if black_color else 1
	
	for tag in results:
		#check if tag is black
		if tag.tag_id % 2 == int(check_black) and tag.tag_id != pawn_tag_id:
			(min_boundary[0], min_boundary[1], 
			max_boundary[0], max_boundary[1]) = return_col_min_max(min_corner_x_value, 
			max_corner_x_value, tag.corners, 
			min_boundary[0], min_boundary[1], 
			max_boundary[0], max_boundary[1])
			
		if tag.tag_id == pawn_tag_id:
			(min_pawn[0], min_pawn[1], 
			max_pawn[0], max_pawn[1]) = return_col_min_max(min_corner_x_value, 
			max_corner_x_value, tag.corners, 
			min_pawn[0], min_pawn[1], 
			max_pawn[0], max_pawn[1])

    
	m_min, b_min = np.polyfit(min_boundary[0], min_boundary[1],1)
	m_max, b_max = np.polyfit(max_boundary[0], max_boundary[1],1)
	
	pawn_m_min, pawn_b_min = np.polyfit(min_pawn[0], min_pawn[1],1)
	pawn_m_max, pawn_b_max = np.polyfit(max_pawn[0], max_pawn[1],1)
	
	add_polyfit_lines(m_min, b_min, min_boundary[0], min_boundary[1])
	add_polyfit_lines(m_max, b_max, max_boundary[0], max_boundary[1])

	board_boundary_min = [m_min, b_min]
	board_boundary_max = [m_max, b_max]
	
	return [pawn_m_min, pawn_b_min], [pawn_m_max, pawn_b_max], board_boundary_min, board_boundary_max
	
			
def return_col_lines(final_apriltag_results):
	#each line defined by m and b
	col_lines = {}
	col_lines["78"], col_lines["67"], board_boundary_min_79, board_boundary_max_78 = calibrate_col_bounds(final_apriltag_results, black_color = True)
	col_lines["23"], col_lines["34"], board_boundary_min_23, board_boundary_max_12 = calibrate_col_bounds(final_apriltag_results, black_color = False)

	#mid_p_m = (col_lines["67"][0] + col_lines["23"][0])/2
	#mid_p_b = (col_lines["67"][1] + col_lines["23"][1])/2
	
	add_polyfit_lines_col(col_lines["67"][0], col_lines["67"][1])
	add_polyfit_lines_col(col_lines["23"][0], col_lines["23"][1])
	
	col_lines["45"] = avg_polyfit_line(col_lines["67"][0], col_lines["67"][1], col_lines["23"][0], col_lines["23"][1])
	col_lines["56"] = avg_polyfit_line(col_lines["67"][0], col_lines["67"][1], col_lines["45"][0], col_lines["45"][1])
	col_lines["34"] = avg_polyfit_line(col_lines["45"][0], col_lines["45"][1], col_lines["23"][0], col_lines["23"][1])

	return col_lines

def sort_row_tags(results, tag_id_num):
	tag3s = [tag for tag in results if tag.tag_id == tag_id_num]

	# Sort by center y-coordinate (center[1])
	sorted_tag3s = sorted(tag3s, key=lambda tag: tag.center[1])

	return sorted_tag3s

def return_row_lines(april_tag_results):
	row_lines = {}
	sorted_rows = {}
	rows = {}
	for i in range(2, 10):
		sorted_rows[i] = sort_row_tags(april_tag_results, i)

	print(sorted_rows)

	max_black_rook = sorted(sorted_rows[4], key=lambda tag: tag.center[1])[1]
	max_white_rook = sorted(sorted_rows[5], key=lambda tag: tag.center[1])[1]
	min_black_rook = sorted(sorted_rows[4], key=lambda tag: tag.center[1])[0]
	min_white_rook = sorted(sorted_rows[5], key=lambda tag: tag.center[1])[0]
	rows['A'] = [max_black_rook, max_white_rook]
	rows['H'] = [max_black_rook, max_white_rook, sorted(sorted_rows[2], key=lambda tag: tag.center[1])[0], sorted(sorted_rows[3], key=lambda tag: tag.center[1])[0]]

	#for letter in rows:
		#get_row_tags(april_tag_results, letter)

	return row_lines


def add_polyfit_lines(m, b, boundary_x, boundary_y):
				
	img = cv2.imread(IMG_PATH)
	num_pixels_y = img.shape[1]
	
	x1, y1 = 0, int(b)
	x2, y2 = num_pixels_y, int(m * num_pixels_y + b)
	cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0) ,5)
	for i in range(len(boundary_x)):
		cv2.circle(img, (int(boundary_x[i]), int(boundary_y[i])), 10, (0, 0, 255), -1)
	
	cv2.imwrite(IMG_PATH, img)
	
def add_polyfit_lines_col(m, b):
				
	img = cv2.imread(IMG_PATH)
	num_pixels_y = img.shape[1]
	x1, y1 = 0, int(b)
	x2, y2 = num_pixels_y, int(m * num_pixels_y + b)
	cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0) ,5)
	
	cv2.imwrite(IMG_PATH, img)
	
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
		if len(results) > num_tags:
			num_tags = len(results)
			final_apriltag_results = results
	
	print(f"Number Tags: {num_tags}")
	#for tag in final_apriltag_results:
	# 	print(f"April Tag ID: {tag.tag_id} , Center: {tag.center} ") #, Corners: {tag.corners}")	
	
	col_lines = return_col_lines(final_apriltag_results)
	print(col_lines)
	print(return_row_lines(final_apriltag_results))

	
	camera.close()
