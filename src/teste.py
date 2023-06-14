import numpy as np



array = ['a', 'b', 'f', 'd', 'e', 'c', 'a', 'g']
reference_values = ['a', 'b', 'c', 'd', 'e', 'f', 'g']

mean_distance = calculate_mean_distance_with_reference(array, reference_values)
print("Mean Distance:", mean_distance)