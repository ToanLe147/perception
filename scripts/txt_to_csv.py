# This script is used to convert from txt annotation to csv labels of Ts
import csv
import os
from PIL import Image
import sys
sys.path.append('..')


def txt2csv(name):
    with open(name, "r") as file:
        stripped = [line.strip() for line in file]
        lines = [line.split(" ") for line in stripped if line]

        size = []
        label = ['Adidas']

        for line in lines:

            image = Image.open("./images_backup/" + line[0])
            width, height = image.size
            size.append([width, height])
            del line[2]
            line[2:2] = [width, height]

            for i in range(2, len(line)):
                line[i] = int(line[i])

            if line[1] != label[-1]:
                label.append(line[1])
        print(label)

        with open('./labels/logos_labels.csv', 'w') as out_file:
            writer = csv.writer(out_file)
            writer.writerow(('filename', 'class', 'width', 'height', 'xmin', 'ymin', 'xmax', 'ymax'))
            writer.writerows(lines)


def main():
    my_dir = os.path.join(os.getcwd(), 'labels')
    for filename in os.listdir(my_dir):
        if ".txt" in filename:
            name = os.path.join(my_dir, filename)
    txt2csv(name)
    print("Created Labels File")


main()
