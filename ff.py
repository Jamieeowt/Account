import numpy as np

# Create the 2D numpy array
array_2D = np.array([
    [1, 2, 3, 4, 5, 6],
    [0, 1, 2, 3, 5, 8],
    [1, 3, 6, 10, 15, 21]
])

# Perform the slice
result = array_2D[:, 0:7:3]

# Print the output
print(result)