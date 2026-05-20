import math
import numpy as np

def get_distance(p1, p2):
    """Calculate Euclidean distance between two (x,y) points."""
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def map_coordinates(value, in_min, in_max, out_min, out_max):
    """Maps a value from one range to another (like Arduino's map function)."""
    # Constrain value to input range
    value = max(min(value, in_max), in_min)
    return out_min + ((value - in_min) / (in_max - in_min)) * (out_max - out_min)