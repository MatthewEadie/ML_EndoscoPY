# import PyQt5
# from PyQt5 import QtWidgets
# from qtwidgets import Toggle, AnimatedToggle

# class Window(QtWidgets.QMainWindow):

#     def __init__(self):
#         super().__init__()

#         toggle_1 = Toggle()
#         toggle_2 = AnimatedToggle(
#             checked_color="#FFB000",
#             pulse_checked_color="#44FFB000"
#         )

#         container = QtWidgets.QWidget()
#         layout = QtWidgets.QVBoxLayout()
#         layout.addWidget(toggle_1)
#         layout.addWidget(toggle_2)
#         container.setLayout(layout)

#         self.setCentralWidget(container)


# app = QtWidgets.QApplication([])
# w = Window()
# w.show()
# app.exec_()

import numpy as np

arr = np.zeros((256,256,1))
arr1 = np.zeros((256,256,1))
arr2 = np.zeros((256,256,1))
arr3 = np.zeros((256,256,1))

a = []

a.append(arr)
a.append(arr1)
a.append(arr2)
a.append(arr3)

print(len(a))

a.pop(0)

a.append(arr)

print(len(a))