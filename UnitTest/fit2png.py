# coding: utf-8
import sys
import os
sys.path.append(os.path.dirname(sys.path[0]))


from astropy.io import fits
import cv2
# import matplotlib.pyplot as plt
# import numpy as np

# f = open("yueshi1.fit", 'rb')
dfu = fits.open("yueshi1.fit")
image_data = dfu[0].data
# image_data.dtype('u2')
print(image_data.shape)

# Pending...
rgb_image = cv2.cvtColor(image_data, cv2.COLOR_BAYER_BG2RGB)
(height, width, _) = rgb_image.shape
rgb_image = cv2.resize(rgb_image, (int(width*0.1),int(height*0.1)))
cv2.imwrite('yueshi1.png', rgb_image)

# rgb_image = cv2.cvtColor(image_data, cv2.COLOR_BAYER_RG)

# # Success
# bin_image = cv2.cvtColor(image_data, cv2.COLOR_BAYER_BG2GRAY)
# print(bin_image.shape)
#
# # xyz_image = cv2.cvtColor(image_data, cv2.COLOR_B)
#
# # plt.imshow(rgb_image)
# # plt.axis("off")
# # plt.savefig("yueshi1.png", bbox_inches='tight')
#
# plt.imshow(bin_image, cmap="gray")
# plt.axis("off")
# plt.savefig("yueshi1_gray.jpg", bbox_inches='tight')
