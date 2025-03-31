from audio.listener import Listener
# from test_frame import Picture
from engine.engine import Engine

# install pyserial to communciate with esp32
# ls /dev/tty* -> shows the port it is running on


def main():

    # intialize class instances
    listener = Listener()
    # picture = Picture()
    engine = Engine(black_playing=True, white_playing=True)

    turn = False

    # Capture and detect AprilTag
    print("Taking picture")
    # before = picture.takePicture()
    # idk what we should do with before from here
    # store it somewhere?
    while True:
        # Get coordinates
        print("Getting coordinates")
        from_coord, to_coord = listener.get_coordinate_input()
        print("Coordinates:", from_coord, to_coord)

        # send the coordinates to the esp32
        listener.communicate_esp(from_coord, to_coord)

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
    print("After picture")
    # after = picture.takePicture()


if __name__ == "__main__":
    main()
