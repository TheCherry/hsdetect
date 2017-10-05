import cv2
import time
import pyautogui
from libs import screen
import numpy as np

import mss

s = mss.mss()

def shot():
    img = s.grab(s.monitors[2])
    return img

def save(img, path):
    mss.tools.to_png(img.rgb, img.size, path)

def simple_compare(img1, img2):
    hist1 = cv2.calcHist([img1],[0],None,[256],[0,256])
    hist2 = cv2.calcHist([img2],[0],None,[256],[0,256])
    ret = cv2.compareHist(hist1,hist2,cv2.HISTCMP_BHATTACHARYYA)
    return ret < 0.007
