from audio.listener import Listener
from test_frame import Picture


def main():

    # intialize class instances
    listener = Listener()
    picture = Picture()

    # Capture and detect AprilTag
    print("Taking picture")
    before = picture.takePicture()
    # idk what we should do with before from here
    # store it somewhere?

    # Call the chess engine HERE!!!

    # Get coordinates
    print("Getting coordinates")
    from_coord, to_coord = listener.get_coordinate_input()
    print("Coordinates:", from_coord, to_coord)

    # send the coordinates to the motor and move the piece accordingly

    # capture an image after the move has been made
    print("After picture")
    after = picture.takePicture()


if __name__ == "__main__":
    main()
