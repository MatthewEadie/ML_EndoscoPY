import numpy as np
import matplotlib.pyplot as plt
import os
import tensorflow as tf
from cv2 import imwrite
from math import floor
import time

from utils import commonFunctions as CF


from cameraSettings import CameraThread
from imageRecorder import ImageRecorder


from PyQt5.QtCore import *
from PyQt5.QtGui import QImage, QPixmap

class machineLearningPipeline(QObject):