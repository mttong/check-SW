import time
from audio.listener import Listener
# from test_frame import Picture
from engine.engine import Engine
from motor.gantry_serial import Gantry
#import motor.constants as constants
from motor import constants
from LCD_Module_RPI_code.RaspberryPi.python.example.lcd import LCD

# install pyserial to communciate with esp32
# ls /dev/tty* -> shows the port it is running on


def main():

    # intialize class instances
    listener = Listener()
    # picture = Picture()
    engine = Engine(black_playing=True, white_playing=True)
    lcd_display = LCD()
    gantry = Gantry()
    
    gantry.set_esp_port()
    gantry.cmd_home(constants.GANTRY)
    
    while gantry.cmd_is_homing(constants.GANTRY):
        time.sleep(0.1)
        
    print("done homing")

    turn = False
    
    #lcd_display.display_ip_address()
    #lcd_display.run()

    # Capture and detect AprilTag
    #print("Taking picture")
    # before = picture.takePicture()
    # idk what we should do with before from here
    # store it somewhere?
    while True:
        # Get coordinates
        print("Getting coordinates")
        from_coord, to_coord = listener.get_coordinate_input()
        print("Coordinates:", from_coord, to_coord) # A2 A4
        
        start_x, start_y, start_z = gantry.chess_to_mm(from_coord, "k")
        end_x, end_y, end_z = gantry.chess_to_mm(to_coord, "k")
        
        gantry.cmd_move_xyz(start_x, start_y, 0)
        
        while gantry.cmd_is_moving(constants.GANTRY):
            time.sleep(0.1)
            
        gantry.cmd_move_xyz(start_x, start_y, start_z)
        
        while gantry.cmd_is_moving(constants.GANTRY):
            time.sleep(0.1)
            
        gantry.cmd_enable_mag(True)
        input()
        
        gantry.cmd_move_xyz(start_x, start_y, 100)
        
        while gantry.cmd_is_moving(constants.GANTRY):
            time.sleep(0.1)
        
        gantry.cmd_move_xyz(end_x, end_y, 100)
        
        while gantry.cmd_is_moving(constants.GANTRY):
            time.sleep(0.1)
            
        gantry.cmd_move_xyz(end_x, end_y, start_z)
        
        while gantry.cmd_is_moving(constants.GANTRY):
            time.sleep(0.1)
            
        gantry.cmd_enable_mag(False)
        
        input()

        # Call the chess engine HERE!!!
        # odd turns be black
        if not turn:
            engine.move_white(from_coord.lower() + to_coord.lower())
        else:
            engine.move_black(from_coord.lower() + to_coord.lower())

        engine.print_board()

        turn = not turn

    # send the coordinates to the motor and move the piece accordingly

    # capture an image after the move has been made
    #print("After picture")
    # after = picture.takePicture()


if __name__ == "__main__":
    main()
