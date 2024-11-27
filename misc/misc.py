# Define the new sigmoid function with adjusted steepness
import numpy as np
from matplotlib import pyplot as plt

import slo_config

center = 500
k = 0.015

x = np.linspace(0, 1000, 500)
# plt.figure(figsize=(10, 6))
# plt.xlim(0,1000)
# plt.ylim(0,1)
# plt.plot(x, utils.sigmoid(x, k, center), color='purple')
plt.plot(x, slo_config.linear(x), color='purple')
plt.axvline(center, color='gray', linestyle=':')
plt.grid()
plt.show()
