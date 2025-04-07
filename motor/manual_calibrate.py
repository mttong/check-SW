from gantry_serial import Gantry
import constants as constants
import time

def print_options():
    print("[0] - Run move relative")
    print("[1] - Select Axis")
    print("[2] - Set Distance mm")
    print("[3] - Enable Magnet")
    print("[4] - Print Coordinates")
    print("[5] - Home axis")
    print("[6] - Home Gantry")

def print_coords(x,y,z):
    print(f'X: {x}')
    print(f'Y: {y}')
    print(f'Z: {z}')

def to_str(axis):
    if axis == 0:
        return "Gantry"
    if axis == 1:
        return "X"
    if axis == 2:
        return "Y"
    if axis == 3:
        return "Z"
    
    
    


def main():
    gant = Gantry()
    gant.set_esp_port()

    last_axis = constants.X_AXIS
    last_d = 0
    mag_state = False

    while True:
        try:
            print(f'Currently: AXIS: {to_str(last_axis)} MM: {last_d} MAG: {"ON" if mag_state else "OFF"}')
            print_options()
            selection = input("Enter: ")
            if selection == "0":
                gant.cmd_move_relative(last_axis, last_d)
                while gant.cmd_is_moving(constants.GANTRY):
                    time.sleep(0.05)
            elif selection == "1":
                axis = input("Enter G, X, Y, Z: ")
                if axis == "G":
                    last_axis = constants.GANTRY
                elif axis == "X":
                    last_axis = constants.X_AXIS
                elif axis == "Y":
                    last_axis = constants.Y_AXIS
                elif axis == "Z":
                    last_axis = constants.Z_AXIS
            elif selection == "2":
                dist = input("Enter mm: ")
                last_d = float(dist)
            elif selection == "3":
                mag_state = not mag_state
                gant.cmd_enable_mag(mag_state)
            elif selection == "4":
                x = gant.cmd_get_posn(constants.X_AXIS)
                y = gant.cmd_get_posn(constants.Y_AXIS)
                z = gant.cmd_get_posn(constants.Z_AXIS)
                print_coords(x,y,z)
            elif selection == "5":
                gant.cmd_home(last_axis)
                while gant.cmd_is_homing(constants.GANTRY):
                    time.sleep(0.05)
            elif selection == "6":
                gant.cmd_home(constants.GANTRY)
                while gant.cmd_is_homing(constants.GANTRY):
                    time.sleep(0.05)
        except KeyboardInterrupt:
            print("Quitting...")
            return
        except Exception as e:
            print("SOMETHING WENT WRONG")
            print(e)
   
if __name__ == "__main__":
    main()
