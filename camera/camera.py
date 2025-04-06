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
	
	# add_polyfit_lines(m_min, b_min, min_boundary[0], min_boundary[1])
	# add_polyfit_lines(m_max, b_max, max_boundary[0], max_boundary[1])
	# add_polyfit_lines(pawn_m_min, pawn_b_min, min_pawn[0], min_pawn[1])
	# add_polyfit_lines(pawn_m_max, pawn_b_max, max_pawn[0], max_pawn[1])

	board_boundary_min = [m_min, b_min]
	board_boundary_max = [m_max, b_max]
	
	return [pawn_m_min, pawn_b_min], [pawn_m_max, pawn_b_max], board_boundary_min, board_boundary_max

def shift_polyfit_x(polyfit_line, shift):
	polyfit_line[1] = polyfit_line[1] - (polyfit_line[0] * shift)
	return polyfit_line
			
def return_col_lines(final_apriltag_results):
	#each line defined by m and b
	col_lines = {}
	min_78, col_lines["67"], boundary_89, max_78 = calibrate_col_bounds(final_apriltag_results, black_color = True)
	col_lines["23"], min_12, max_12, boundary_01 = calibrate_col_bounds(final_apriltag_results, black_color = False)

	#shift boundary line next to column 1 30 pixels to the right
	col_lines["01"] = shift_polyfit_x(boundary_01, 30)
	#shift boundary line next to column 8 to the left by 30 pixels
	col_lines["89"] = shift_polyfit_x(boundary_89, -30)

	col_lines["12"] = avg_x_polyfit_line(min_12[0], min_12[1], max_12[0], max_12[1])
	col_lines["78"] = avg_x_polyfit_line(min_78[0], min_78[1], max_78[0], max_78[1])

	col_lines["23"] = shift_polyfit_x([col_lines["23"][0], col_lines["23"][1]], -20)
	col_lines["67"] = shift_polyfit_x([col_lines["67"][0], col_lines["67"][1]], 20)

	col_lines["45"] = avg_x_polyfit_line(col_lines["67"][0], col_lines["67"][1], col_lines["23"][0], col_lines["23"][1])
	col_lines["56"] = avg_x_polyfit_line(col_lines["67"][0], col_lines["67"][1], col_lines["45"][0], col_lines["45"][1])
	col_lines["34"] = avg_x_polyfit_line(col_lines["45"][0], col_lines["45"][1], col_lines["23"][0], col_lines["23"][1])

	return col_lines

def sort_row_tags(results, tag_id_num):
	tag3s = [tag for tag in results if tag.tag_id == tag_id_num]

	# Sort by center y-coordinate (center[1])
	sorted_tag3s = sorted(tag3s, key=lambda tag: tag.center[1])

	return sorted_tag3s

def return_min_max_line_rows(results):
	min_boundary = [np.array([]), np.array([])]
	max_boundary = [np.array([]), np.array([])]

	min_corner_y_value = 1944.0 #size of the image
	max_corner_y_value = 0.0

	for tag in results:
		min_corner_y = min_corner_y_value
		min_corner = []
		max_corner_y = max_corner_y_value
		max_corner = []
		for corner in tag.corners:
			if corner[1] < min_corner_y:
				min_corner_y = corner[1]
				min_corner = corner
			if corner[1] > max_corner_y:
				max_corner_y = corner[1]
				max_corner = corner
		min_boundary[1] = np.append(min_boundary[1], min_corner_y)
		min_boundary[0] = np.append(min_boundary[0], min_corner[0])
		max_boundary[1] = np.append(max_boundary[1], max_corner_y)
		max_boundary[0] = np.append(max_boundary[0] , max_corner[0])	


	m_min, b_min = np.polyfit(min_boundary[0], min_boundary[1],1)
	m_max, b_max = np.polyfit(max_boundary[0], max_boundary[1],1)

	min_line = [m_min, b_min]
	max_line = [m_max, b_max]

	return (min_line, max_line)

def return_row_lines(april_tag_results):
	row_lines = {}
	sorted_rows = {}
	rows = {}
	for i in range(2, 14):
		sorted_rows[i] = sort_row_tags(april_tag_results, i)

	row_letters = 'HGFEDCBA'

	min_black_rook = sorted(sorted_rows[4], key=lambda tag: tag.center[1])[0]
	max_black_rook = sorted(sorted_rows[4], key=lambda tag: tag.center[1])[1]
	min_white_rook = sorted(sorted_rows[5], key=lambda tag: tag.center[1])[0]
	max_white_rook = sorted(sorted_rows[5], key=lambda tag: tag.center[1])[1]

	min_black_bishop = sorted(sorted_rows[6], key=lambda tag: tag.center[1])[0]
	max_black_bishop = sorted(sorted_rows[6], key=lambda tag: tag.center[1])[1]
	min_white_bishop = sorted(sorted_rows[7], key=lambda tag: tag.center[1])[0]
	max_white_bishop = sorted(sorted_rows[7], key=lambda tag: tag.center[1])[1]

	min_black_knight = sorted(sorted_rows[8], key=lambda tag: tag.center[1])[0]
	max_black_knight = sorted(sorted_rows[8], key=lambda tag: tag.center[1])[1]
	min_white_knight = sorted(sorted_rows[9], key=lambda tag: tag.center[1])[0]
	max_white_knight = sorted(sorted_rows[9], key=lambda tag: tag.center[1])[1]

	min_black_queen = sorted(sorted_rows[10], key=lambda tag: tag.center[1])[0]
	min_white_queen = sorted(sorted_rows[11], key=lambda tag: tag.center[1])[0]
	min_black_king = sorted(sorted_rows[12], key=lambda tag: tag.center[1])[0]
	min_white_king = sorted(sorted_rows[13], key=lambda tag: tag.center[1])[0]

	rows['A'] = [max_black_rook, max_white_rook]
	rows['B'] = [max_black_knight, max_white_knight]
	rows['C'] = [max_black_bishop, max_white_bishop]
	rows['D'] = [min_black_queen, min_white_queen]
	rows['E'] = [min_black_king, min_white_king]
	rows['F'] = [min_black_bishop, min_white_bishop]
	rows['G'] = [min_black_knight, min_white_knight]
	rows['H'] = [min_black_rook, min_white_rook]
	for i in range(8):
		rows[row_letters[i]].append(sorted(sorted_rows[2], key=lambda tag: tag.center[1])[i])
		rows[row_letters[i]].append(sorted(sorted_rows[3], key=lambda tag: tag.center[1])[i])

####START EDITING HERE
		min_line, max_line = return_min_max_line_rows(rows[row_letters[i]])

	print("row lines", row_lines)
	AB_line = avg_y_polyfit_line(row_lines[0], row_lines[1])
	add_polyfit_lines(AB_line)

	
	#for letter in rows:
		#get_row_tags(april_tag_results, letter)

	return row_lines


def add_polyfit_lines_circle(m, b, boundary_x, boundary_y):
				
	img = cv2.imread(IMG_PATH)
	num_pixels_y = img.shape[1]
	
	x1, y1 = 0, int(b)
	x2, y2 = num_pixels_y, int(m * num_pixels_y + b)
	cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0) ,5)
	for i in range(len(boundary_x)):
		cv2.circle(img, (int(boundary_x[i]), int(boundary_y[i])), 10, (0, 0, 255), -1)
	
	cv2.imwrite(IMG_PATH, img)
	
def add_polyfit_lines(polyfit_line):
	m = polyfit_line[0]
	b = polyfit_line[1]
				
	img = cv2.imread(IMG_PATH)
	num_pixels_y = img.shape[1]
	x1, y1 = 0, int(b)
	x2, y2 = num_pixels_y, int(m * num_pixels_y + b)
	cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0) ,5)
	
	cv2.imwrite(IMG_PATH, img)
	
def avg_x_polyfit_line(m_max, b_max, m_min, b_min):
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
	# add_polyfit_lines([m_avg, b_avg])
	return m_avg, b_avg

def avg_y_polyfit_line(max_line, min_line):
	m_max = max_line[0]
	b_max = max_line[1]
	m_min = min_line[0]
	b_min= min_line[1]
	#TODO: 1944 = image size, remove hard coded value
	x_values = np.arange(1944)
    
    # Calculate x-values for both lines at each y
	max_y = m_max * x_values + b_max
	min_y = m_min * x_values + b_min
    
    # Average the x-values at each y-coordinate
	avg_y = (max_y + min_y) / 2
    
    # Fit new line through (avg_x, y_values) points
	valid = np.isfinite(avg_y)
	m_avg, b_avg = np.polyfit(x_values[valid], avg_y[valid], 1)
	# add_polyfit_lines([m_avg, b_avg])
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
	for line_num, line_value  in col_lines.items():
		add_polyfit_lines(line_value)

	print(return_row_lines(final_apriltag_results))

	
	camera.close()
