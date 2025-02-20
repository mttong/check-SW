from picamera2 import Picamera2
import cv2
import time
import pupil_apriltags as apriltag
# import apriltag


class Picture:
    def __init__(self, image_path="/home/check/Documents/image.jpg", tag_family="tag36h11"):
        self.image_path = image_path
        self.tag_family = tag_family
        self.camera = Picamera2()

    def takePicture(self):
        config = self.camera.create_still_configuration(raw={}, display=None)
        self.camera.configure(config)

        self.camera.start()
        time.sleep(2)
        self.camera.capture_file(self.image_path)
        img = cv2.imread(self.image_path)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        detector = apriltag.Detector(families="tag36h11")
        results = detector.detect(gray)

        print(results)

        print("Done.")
        self.camera.close()
        return results


if __name__ == "__main__":
    picture = Picture()
    results = picture.takePicture()
