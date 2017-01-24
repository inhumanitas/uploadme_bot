#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2

import logging
import os
import sys
import numpy as np
from PIL import Image


MALE = 1
FEMALE = 2

# Для детектирования лиц используем каскады Хаара
cascadePath = "haarcascade_frontalface_default.xml"

base_path = os.path.dirname(__file__)

faceCascade = cv2.CascadeClassifier(
    os.path.join(
        base_path,
        'haarcascade_frontalface_default.xml')
)

# Для распознавания используем локальные бинарные шаблоны
recognizer = cv2.createLBPHFaceRecognizer(1, 8, 8, 8, 123)

logger = logging.getLogger(__name__)


def get_face(image_path):
    # Переводим изображение в черно-белый формат и
    # приводим его к формату массива

    gray = Image.open(image_path).convert('L')

    image = np.array(gray, 'uint8')

    # Определяем области где есть лица
    return faceCascade.detectMultiScale(
            image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)), image


def get_images(path):
    # Ищем все фотографии и записываем их в image_paths
    image_paths = [os.path.join(path, f) for f in os.listdir(path)]
    images = []

    for image_path in image_paths:
        faces, image = get_face(image_path)
        # images.append(image)
        for (x, y, w, h) in faces:
            images.append(image[y: y + h, x: x + w])

    print len(image_paths), len(images)
    return images

# Получаем лица и соответствующие им номера
male_images = get_images(os.path.join(base_path, 'gender_recognition/male'))
female_images = get_images(
    os.path.join(base_path, 'gender_recognition/female'))


cv2.destroyAllWindows()

# Обучаем программу распознавать лица
recognizer.train(
    male_images + female_images,
    np.array([MALE] * len(male_images) + [FEMALE] * len(female_images)))


def recog(image_path):
    m, f = 0, 0
    m_c, f_c = 0, 0
    # Ищем лица на фотографиях
    faces, image = get_face(image_path)
    for (x, y, w, h) in faces:
        # Если лица найдены, пытаемся распознать их
        # Функция  recognizer.predict в случае успешного расознавания
        # возвращает номер и параметр confidence, этот параметр указывает
        # на уверенность алгоритма, что это именно тот человек,
        # чем он меньше, тем больше уверенность
        number_predicted, conf = recognizer.predict(
            image[y: y + h, x: x + w])
        # cv2.imshow("Recognizing Face", image[y: y + h, x: x + w])
        # cv2.waitKey(1000)

        if number_predicted == MALE:
            m += 1
            m_c += conf
        else:
            f += 1
            f_c += conf
    if m_c < 0 or f_c < 0:
        result = image_path, u'неопределил', m_c
    elif m >= f:
        result = image_path, u'мужик', m_c
    else:
        result = image_path, u'женщина', f_c
    logger.info(unicode(result))
    return result

if __name__ == '__main__':
    # Создаем список фотографий для распознавания
    for img_path in sys.argv[1:]:
        print recog(img_path)
