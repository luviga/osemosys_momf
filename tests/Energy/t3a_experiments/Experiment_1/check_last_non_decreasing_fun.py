from copy import deepcopy



# Input list
lst = [
    22.1456, 24.2025, 26.4833, 27.9663, 29.5055, 31.1009, 32.2455,
    32.7879, 33.529, 34.235, 34.8853, 35.4704, 35.978, 36.4151,
    36.7907, 37.1276, 37.427, 37.6764, 37.8232, 37.8174, 37.6472,
    37.4084, 37.2599, 37.3418, 37.6926, 38.2769, 39.0411, 39.9276,
    40.905, 41.9446, 43.0368, 44.1693, 45.3423
]

lst_raw = deepcopy(lst)

# Initialize the last non-decreasing value with the first element of the list
last_non_decreasing_value = lst[0]

# Iterate through the list starting from the second element
for i in range(1, len(lst)):
    # If the current element is less than the last non-decreasing value,
    # update it to the last non-decreasing value
    if lst[i] < last_non_decreasing_value:
        lst[i] = last_non_decreasing_value
    else:
        # Otherwise, update the last non-decreasing value to the current element
        last_non_decreasing_value = lst[i]

# Print the modified list
for value in lst:
    print(value)
