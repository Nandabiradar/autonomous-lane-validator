# Simulation Log Analysis

This project implements a function to analyze car trajectories and determine if a car stayed within lane boundaries during simulation.

## Files

- `sim_log_analysis.py` - Contains the main `car_stayed_in_lane()` function
- `test_car_lane_analysis.py` - Unit tests for the lane analysis function
- `requirements.txt` - Required Python packages

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

The main function `car_stayed_in_lane()` takes three parameters:

- `lane_left`: List of (x,y) tuples representing the left lane boundary
- `lane_right`: List of (x,y) tuples representing the right lane boundary  
- `car_path`: List of (x,y) tuples representing the car's trajectory

Returns `True` if the car stayed within the lane boundaries, `False` otherwise.

```python
from sim_log_analysis import car_stayed_in_lane

# Example usage
lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0)]
lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0)]
car_path = [(4.0, 0.0), (4.0, 1.0), (4.0, 2.0)]

result = car_stayed_in_lane(lane_left, lane_right, car_path)
print(result)  # True - car stayed in lane
```

## Running Tests

Run the test suite:

```bash
python test_car_lane_analysis.py
```

For verbose output:

```bash
python test_car_lane_analysis.py -v
```

## Implementation Details

The function uses:
- NumPy for efficient array operations
- SciPy for spline interpolation between lane boundary points
- Linear interpolation to determine lane boundaries at each car position
- Boundary checking to verify the car stays within the lane 