import matplotlib.pyplot as plt
import numpy as np

# red : high, green : med, blue : low

h = np.random.rand(50)
m = np.random.rand(50)
l = np.random.rand(50)

ha = np.random.rand(50)
ma = np.random.rand(50)
la = np.random.rand(50)

plt.scatter(h, ha, c='r')
plt.scatter(m, ma, c='g')
plt.scatter(l, la, c='b')
plt.show()
