import hashlib
import threading
import time
from datetime import datetime

import cv2
import matplotlib
from easyocr import easyocr
from matplotlib import pyplot as plt

import constants
from open_gate import open_gate

from helpers import db
from models import CarNumber, LogCar, AdminSetting

daemon_running = False
plate_cascade = cv2.CascadeClassifier('haarcascade_russian_plate_number.xml')
arr_success = []


def start_daemon():
    global daemon_running
    if not daemon_running:
        daemon_running = True
        daemon_thread = threading.Thread(target=license_plate_recognition_daemon)
        daemon_thread.start()


def stop_daemon():
    global daemon_running
    daemon_running = False


def carplate_extract(image, ):
    carplate_rects = plate_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    arr = []
    for x, y, w, h in carplate_rects:
        arr.append(image[y: y + h, x: x + w])
    return arr


def enlarge_img(image, scale_percent):
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resized_image


def license_plate_recognition_daemon():
    from app import app
    with app.app_context():
        matplotlib.use('agg')
        global daemon_running
        global arr_success
        arr_success = {}
        start = time.time()
        i = 0
        camera_path = AdminSetting.query.filter_by(key='camera_url').first()
        if camera_path:
            video_capture = cv2.VideoCapture(camera_path.value)
            while daemon_running:
                if not video_capture:
                    camera_path = AdminSetting.query.filter_by(key='camera_url').first()
                    if camera_path:
                        video_capture = cv2.VideoCapture(camera_path.value)

                ret, frame = video_capture.read()
                if not ret:
                    video_capture.release()
                    check_path = AdminSetting.query.filter_by(key='camera_url').first()
                    if check_path.value != camera_path.value:
                        video_capture = cv2.VideoCapture(check_path.value)
                        camera_path = check_path
                        continue
                    else:
                        video_capture = None
                        continue
                if i % 20 == 0:
                    carplate_img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    carplate_extract_img = carplate_extract(carplate_img_rgb)

                    for nomer in carplate_extract_img:
                        carplate_extract_img = enlarge_img(nomer, 200)
                        carplate_extract_img_gray = cv2.cvtColor(carplate_extract_img, cv2.COLOR_RGB2GRAY)

                        # carplate_extract_img_gray_blur = cv2.medianBlur(carplate_extract_img_gray, 3)
                        # img_gaussian = cv2.GaussianBlur(
                        #     carplate_extract_img_gray_blur, (5, 5), 0)

                        reader = easyocr.Reader(['en', 'ru'])
                        result_easyocr = reader.readtext(carplate_extract_img_gray, detail=1, paragraph=False, width_ths=10, height_ths=0.8,
                                                         slope_ths=0.3, allowlist='ABCEHKMOPTXY0123456789', blocklist='!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~«»',
                                                         min_size=30)
                        if len(result_easyocr) > 0:
                            for result in result_easyocr:
                                result_str = result[1]
                                result_str = ''.join(filter(lambda x: x.isalnum(), result_str))
                                result_str = result_str.upper()
                                if 8 <= len(result_str) <= 9:
                                    if result_str[0].isalpha() and result_str[1].isdigit() and result_str[2].isdigit() and \
                                            result_str[3].isdigit() and result_str[4].isalpha() and \
                                            result_str[5].isalpha() and result_str[6].isdigit() and result_str[7].isdigit() and \
                                            (len(result_str) == 8 or result_str[8].isdigit()):
                                        if result_str not in arr_success or time.time() - arr_success[result_str] > constants.CAR_NUMBER_DETECTION_TIMEOUT:
                                            arr_success[result_str] = time.time()
                                            print(i, result[1], result[2])
                                            car_number = CarNumber.query.filter_by(car_number=result_str).first()
                                            if car_number:
                                                if car_number.status == constants.CAR_NUMBER_STATUS_ACTIVE and (
                                                        car_number.type == constants.CAR_NUMBER_TYPE_PERMANENT or
                                                        (
                                                            car_number.type == constants.CAR_NUMBER_TYPE_TEMPORARY and
                                                            car_number.date_start < datetime.now() and
                                                            (
                                                                not car_number.date_end or car_number.date_end > datetime.now())
                                                        ) or
                                                        (
                                                                car_number.type == constants.CAR_NUMBER_TYPE_ONE_TIME and
                                                                car_number.total_count < 2 and
                                                                car_number.date_start < datetime.now()
                                                        )
                                                ):
                                                    car_number.total_entries += 1
                                                    date_detected = datetime.now()
                                                    hash_obj = hashlib.md5(f'{car_number.id}_{date_detected}'.encode('utf-8'))
                                                    hash_file_name = hash_obj.hexdigest()
                                                    log_car = LogCar(car_number_id=car_number.id, date=date_detected, hash_name=hash_file_name)
                                                    db.session.add(log_car)
                                                    db.session.commit()

                                                    cv2.imwrite(f'static/img/original_{hash_file_name}.png', frame)
                                                    cv2.imwrite(f'static/img/carplate_{hash_file_name}.png', carplate_extract_img_gray)
                                                    # open_gate()
                i += 1

            fps = video_capture.get(cv2.CAP_PROP_FPS)
            frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps
            print(time.time() - start, fps, frame_count, duration)
            video_capture.release()
