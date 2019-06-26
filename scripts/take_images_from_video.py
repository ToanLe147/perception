# This file take image from video and splits the imgaes into 3 folders
#
import cv2
import os
import random
import sys

sys.path.append('..')
dir = ['./images_set', './images_set/testing', './images_set/validating', './images_set/images']

# Create directories if they are not available
if not len(os.listdir(dir[0])):
    for i in range(1, len(dir)):
        os.mkdir(dir[i])
        print("{} is created".format(dir[i]))

# Generate images from testing video
vidcap = cv2.VideoCapture('./video/test_nokia.mp4')
success, image = vidcap.read()
count = 0
while success:
    success, image = vidcap.read()
    if success:
        cv2.imwrite('./images_set/images/frame%d.jpg' % count, image)
        if cv2.waitKey(10) == 27:
            break
        count += 1

list_of_images = os.listdir(dir[3])
print(list_of_images)
total_images = len(list_of_images)

# Take 15% for validation and 15% for testing
testing_num = int(round(0.15 * total_images))
validation_num = int(round(0.15 * total_images))

number_of_image = [total_images, testing_num, validation_num, total_images - (testing_num + validation_num)]

# Sorting testing images
for i in range(1, len(dir) - 1):
    list_of_images = os.listdir(dir[3])
    if not len(os.listdir(dir[i])):
        for image in random.sample(list_of_images, number_of_image[i]):
            old_path = os.path.join(dir[3], image)
            # print(old_path)
            new_path = os.path.join(dir[i], image)
            # print(new_path)
            os.rename(old_path, new_path)
        print(os.listdir(dir[i]))
