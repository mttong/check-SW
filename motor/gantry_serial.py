from serial import Serial
import serial.tools.list_ports
import struct
import constants
import time

class GantryError(Exception):
    """Gantry exceptions."""

    def __init__(self, error_code):
        match error_code:
            case constants.RET_TIMEOUT:
                message = "Command timed out"
            case constants.RET_UNRECOGNIZED:
                message = "Command not recognized"
            case constants.RET_INVALID_PARAM:
                message = "Invalid parameter for command"
            case constants.RET_ERROR:
                message = "Something else went wrong during command"
        super().__init__(message)

class Gantry:
    def __init__(self):
        self.baud = constants.ESP_BAUD
        self._first_cmd = True
        self.esp = None

    def set_esp_port(self, port:str = None):
        """
        Set the port for the ESP32. If no port is given, the port will
        automatically be found.

        :param str port: The port of the ESP32. If not given, automatically found
        :raises RuntimeError: When the port is automatically searched and not found
        """
        if port:
            try:
                self.esp = Serial(port, self.baud)
                time.sleep(5)
                while self.esp.in_waiting > 0:
                    print(self.esp.readline())
            except:
                raise GantryError(constants.RET_ERROR)
            finally:
                if self.esp.is_open:
                    self.esp.close()
            return
        ports = serial.tools.list_ports.comports()
        for p, _, hwid in sorted(ports):
            if constants.ESP_HID_VID in hwid:
                try:
                    self.esp = Serial(p, self.baud)
                    time.sleep(5)
                    while self.esp.in_waiting > 0:
                        print(self.esp.readline())
                except:
                    raise GantryError(constants.RET_ERROR)
                finally:
                    if self.esp.is_open:
                        self.esp.close()
                return
        raise RuntimeError("ESP32 port not found")

    def _get_command_bytes(self, cmd:int, type: int, params) -> bytearray:
        cmd_b = cmd.to_bytes(1, byteorder='big')
        type_b = type.to_bytes(1, byteorder='big')
        command_bytes = bytearray(cmd_b + type_b)
        for param in params:
            added_param = struct.pack("f", param)
            command_bytes += bytearray(added_param)
        return command_bytes
    
    def _decode_response(self, resp: bytearray) -> list[int]:
        ret_list = [int(resp[0])]
        i = 1
        while resp[i] != constants.RET_ENDLINE:
            ret_list.append(struct.unpack("f", resp[i:i+4])[0])
            i += 4
        return ret_list
    
    def _send_command(self, cmd:int, type: int, *params) -> list[int]:
        if self.esp == None:
            raise RuntimeError("ESP32 port not set")
        cmd_bytes = self._get_command_bytes(cmd, type, params)
        try:
            if not self.esp.is_open:
                self.esp.open()
            self.esp.write(cmd_bytes)
            while self.esp.in_waiting == 0:
                pass
            return self._decode_response(self.esp.readline())
        except:
            raise RuntimeError("Error during ESP communication")
        finally:
            self.esp.close()

    def _validate_cmd_type(command_typeself, cmd_type:int):
        if cmd_type < 0 or cmd_type > 4:
            raise ValueError("Invalid command type")

    def cmd_home(self, command_type:int):
        self._validate_cmd_type(command_type)
        ret, = self._send_command(constants.CMD_HOME, command_type)
        if ret:
            raise GantryError(ret)

    def cmd_stop(self, command_type:int):
        self._validate_cmd_type(command_type)
        ret, = self._send_command(constants.CMD_STOP, command_type)
        if ret:
            raise GantryError(ret)

    def cmd_is_homing(self, command_type:int) -> bool:
        self._validate_cmd_type(command_type)
        ret, is_homing = self._send_command(constants.CMD_IS_HOMING, command_type)
        if ret:
            raise GantryError(ret)
        return bool(is_homing)

    def cmd_is_moving(self, command_type:int) -> bool:
        self._validate_cmd_type(command_type)
        ret, is_moving = self._send_command(constants.CMD_IS_MOVING, command_type)
        self._send_command(constants.CMD_IS_MOVING, command_type)
        if ret:
            raise GantryError(ret)
        return bool(is_moving)

    def cmd_get_posn(self, command_type:int) -> float:
        self._validate_cmd_type(command_type)
        ret, posn = self._send_command(constants.CMD_GET_POSN, command_type)
        if ret:
            raise GantryError(ret)
        return posn

    def cmd_get_speed(self, command_type:int) -> float:
        self._validate_cmd_type(command_type)
        ret, speed = self._send_command(constants.CMD_GET_SPEED, command_type)
        if ret:
            raise GantryError(ret)
        return speed

    def cmd_get_default_speed(self, command_type:int) -> float:
        self._validate_cmd_type(command_type)
        ret, speed = self._send_command(constants.CMD_GET_DEFAULT_SPEED, command_type)
        if ret:
            raise GantryError(ret)
        return speed

    def cmd_get_slow_speed(self, command_type:int) -> float:
        self._validate_cmd_type(command_type)
        ret, speed = self._send_command(constants.CMD_GET_SLOW_SPEED, command_type)
        if ret:
            raise GantryError(ret)
        return speed

    def cmd_get_fine_speed(self, command_type:int) -> float:
        self._validate_cmd_type(command_type)
        ret, speed = self._send_command(constants.CMD_GET_FINE_SPEED, command_type)
        if ret:
            raise GantryError(ret)
        return speed

    def cmd_get_max_speed(self, command_type:int) -> float:
        self._validate_cmd_type(command_type)
        ret, speed = self._send_command(constants.CMD_GET_MAX_SPEED, command_type)
        if ret:
            raise GantryError(ret)
        return speed

    def cmd_get_accel(self, command_type:int) -> float:
        self._validate_cmd_type(command_type)
        ret, accel = self._send_command(constants.CMD_GET_ACCEL, command_type)
        if ret:
            raise GantryError(ret)
        return accel

    def cmd_get_limit(self, command_type:int) -> bool:
        self._validate_cmd_type(command_type)
        ret, lim = self._send_command(constants.CMD_GET_LIMIT, command_type)
        if ret:
            raise GantryError(ret)
        return bool(lim)

    def cmd_get_dist_to_go(self, command_type:int) -> float:
        self._validate_cmd_type(command_type)
        ret, dist = self._send_command(constants.CMD_GET_DIST_TO_GO, command_type)
        if ret:
            raise GantryError(ret)
        return dist

    def cmd_get_target_posn(self, command_type:int) -> float:
        self._validate_cmd_type(command_type)
        ret, target_posn = self._send_command(constants.CMD_GET_TARGET_POSN, command_type)
        if ret:
            raise GantryError(ret)
        return target_posn

    def cmd_move_absolute(self, command_type:int, posn:float):
        self._validate_cmd_type(command_type)
        ret, = self._send_command(constants.CMD_MOVE_ABSOLUTE, command_type, posn)
        if ret:
            raise GantryError(ret)

    def cmd_move_relative(self, command_type:int, dist:float):
        self._validate_cmd_type(command_type)
        ret, = self._send_command(constants.CMD_MOVE_RELATIVE, command_type, dist)
        if ret:
            raise GantryError(ret)

    def cmd_set_posn(self, command_type:int, posn:float):
        self._validate_cmd_type(command_type)
        ret, = self._send_command(constants.CMD_SET_POSN, command_type, posn)
        if ret:
            raise GantryError(ret)

    def cmd_set_max_speed(self, command_type:int, speed:float):
        self._validate_cmd_type(command_type)
        ret, = self._send_command(constants.CMD_SET_MAX_SPEED, command_type, speed)
        if ret:
            raise GantryError(ret)

    def cmd_set_default_speed(self, command_type:int, speed:float):
        self._validate_cmd_type(command_type)
        ret, = self._send_command(constants.CMD_SET_DEFAULT_SPEED, command_type, speed)
        if ret:
            raise GantryError(ret)

    def cmd_set_default_speed(self, command_type:int, speed:float):
        self._validate_cmd_type(command_type)
        ret, = self._send_command(constants.CMD_SET_DEFAULT_SPEED, command_type, speed)
        if ret:
            raise GantryError(ret)

    def cmd_set_fine_speed(self, command_type:int, speed:float):
        self._validate_cmd_type(command_type)
        ret, = self._send_command(constants.CMD_SET_FINE_SPEED, command_type, speed)
        if ret:
            raise GantryError(ret)

    def cmd_set_accel(self, command_type:int, accel:float):
        self._validate_cmd_type(command_type)
        ret, = self._send_command(constants.CMD_SET_ACCEL, command_type, accel)
        if ret:
            raise GantryError(ret)

    def cmd_enable_mag(self, enable:bool):
        en = 0
        if enable:
            en = 1
        ret, = self._send_command(constants.CMD_ENABLE_MAG, constants.GANTRY, en)
        if ret:
            raise GantryError(ret)

    def cmd_move_xz(self, command_type:int, x:float, z:float):
        self._validate_cmd_type(command_type)
        ret, = self._send_command(constants.CMD_SET_ACCEL, command_type, x, z)
        if ret:
            raise GantryError(ret)

    def cmd_move_xyz(self, command_type:int, x:float, y:float, z:float):
        self._validate_cmd_type(command_type)
        ret, = self._send_command(constants.CMD_SET_ACCEL, command_type, x, y, z)
        if ret:
            raise GantryError(ret)
