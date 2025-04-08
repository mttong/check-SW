import time
from audio.listener import Listener
# from test_frame import Picture
from engine.engine import Engine
from engine.piece_keeper import PieceKeeper
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
    keeper = PieceKeeper()
    lcd_display = LCD()
    gantry = Gantry()
    
    gantry.set_esp_port()
    gantry.cmd_home(constants.GANTRY)
    
    while gantry.cmd_is_homing(constants.GANTRY):
        lcd_display.motor_calibrating()
        time.sleep(0.1)
        
    print("done homing")

    turn = False
    
    lcd_display.display_default_images()
    #lcd_display.run()

    # Capture and detect AprilTag
    #print("Taking picture")
    # before = picture.takePicture()
    # idk what we should do with before from here
    # store it somewhere?
    while True:
        # Get coordinates
        print("Getting coordinates")
        
        # manual input for testing
        from_coord = input()
        to_coord = input()
        
        
        # from_coord, to_coord = listener.get_coordinate_input()
        print("Coordinates:", from_coord, to_coord) # A2 A4
        
        # Call the chess engine HERE!!!
        # odd turns be black
        if not turn:
            lcd_display.display_turn_white()
            engine.move_white(from_coord.lower() + to_coord.lower())
        else:
            lcd_display.display_turn_black()
            engine.move_black(from_coord.lower() + to_coord.lower())

        engine.print_board()

        turn = not turn
        
        for (from_coord, to_coord), piece in keeper.move(from_coord, to_coord):
            # Convert chess coordinates to mm coordinates
            from_coord = from_coord.upper()
            to_coord = to_coord.upper()
            pick_x, pick_y, pick_z = gantry.chess_to_mm(from_coord, piece)
            place_x, place_y, place_z = gantry.chess_to_mm(to_coord, piece)
            
            # Move above pick coordinate
            gantry.cmd_move_xyz(pick_x, pick_y, constants.SAFE_HEIGHT)
            while gantry.cmd_is_moving(constants.GANTRY):
                time.sleep(0.1)
            
            # Descent to pick position
            gantry.cmd_move_xyz(pick_x, pick_y, pick_z)
            while gantry.cmd_is_moving(constants.GANTRY):
                time.sleep(0.1)
            
            # Enable the electromagnet
            time.sleep(0.1)
            gantry.cmd_enable_mag(True)
            time.sleep(0.4)
            # input() # Added if electromagnet done manually with power supply
            
            # Move straight up with the piece held
            gantry.cmd_move_xyz(pick_x, pick_y, constants.SAFE_HEIGHT)
            while gantry.cmd_is_moving(constants.GANTRY):
                time.sleep(0.1)
            
            # Move above place location
            gantry.cmd_move_xyz(place_x, place_y, constants.SAFE_HEIGHT)
            while gantry.cmd_is_moving(constants.GANTRY):
                time.sleep(0.1)
            
            # Descend down to place the piece
            gantry.cmd_move_xyz(place_x, place_y, place_z)
            while gantry.cmd_is_moving(constants.GANTRY):
                time.sleep(0.1)
            
            # Disable the electromagnet to let go
            time.sleep(0.1)
            gantry.cmd_enable_mag(False)
            time.sleep(0.5)
            # input() # Added if electromagnet done manually with power supply
            
            # Move up to the safe height to prepare for the next move command
            gantry.cmd_move_xyz(place_x, place_y, constants.SAFE_HEIGHT)
            while gantry.cmd_is_moving(constants.GANTRY):
                time.sleep(0.1)


    # send the coordinates to the motor and move the piece accordingly

    # capture an image after the move has been made
    #print("After picture")
    # after = picture.takePicture()


if __name__ == "__main__":
    main()
