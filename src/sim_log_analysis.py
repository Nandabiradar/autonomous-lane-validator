"""
Functions to interpret simulation logs
"""

import numpy as np
from scipy.interpolate import interp1d
from shapely.geometry import Point, Polygon


def car_stayed_in_lane(lane_left, lane_right, car_path, method="hybrid", return_details=False) -> bool | dict:
    """
    Return True if the car trajectory stays inside the lane lines.
    Returns False if the car trajectory goes out of the lane.
    
    Args:
        lane_left: List of (x,y) tuples representing the left lane boundary
        lane_right: List of (x,y) tuples representing the right lane boundary
        car_path: List of (x,y) tuples representing the car's trajectory
        method: Analysis method - "geometric", "interpolation", "hybrid" (default)
        return_details: If True, returns dict with detailed analysis results
    
    Returns:
        bool or dict: True/False if car stayed in lane, or detailed dict if return_details=True
    """
    if not lane_left or not lane_right or not car_path:
        result = {"result": False, "method": method, "reason": "Empty input data"}
        return result if return_details else False
    
    # Special handling for single-point inputs
    if len(car_path) == 1 and len(lane_left) == 1 and len(lane_right) == 1:
        car_x, car_y = car_path[0]
        left_x, left_y = lane_left[0]
        right_x, right_y = lane_right[0]
        
        # For single points, check if car is between left and right boundaries
        # Ensure left is actually to the left of right
        if left_x > right_x:
            left_x, right_x = right_x, left_x
        
        in_lane = left_x <= car_x <= right_x
        result = {
            "result": in_lane,
            "method": "single_point",
            "violations": 0 if in_lane else 1,
            "total_points": 1,
            "min_distance_to_boundary": min(abs(car_x - left_x), abs(car_x - right_x))
        }
        return result if return_details else in_lane
    
    # Route to specific analysis method
    if method == "geometric":
        return _analyze_geometric(lane_left, lane_right, car_path, return_details)
    elif method == "interpolation":
        return _analyze_interpolation(lane_left, lane_right, car_path, return_details)
    elif method == "hybrid":
        return _analyze_hybrid(lane_left, lane_right, car_path, return_details)
    else:
        raise ValueError(f"Unknown method: {method}. Use 'geometric', 'interpolation', or 'hybrid'")


def _analyze_geometric(lane_left, lane_right, car_path, return_details=False):
    """
    Geometric analysis using Shapely polygon containment.
    Fast but may have issues with complex lane shapes.
    """
    try:
        # Create lane polygon by connecting left and right boundaries
        if len(lane_left) < 2 or len(lane_right) < 2:
            # Fall back to simple boundary check for insufficient points
            return _analyze_interpolation(lane_left, lane_right, car_path, return_details)
        
        # Create polygon points: left boundary + reversed right boundary
        polygon_points = lane_left + lane_right[::-1]
        
        # Ensure polygon is closed
        if polygon_points[0] != polygon_points[-1]:
            polygon_points.append(polygon_points[0])
        
        # Create Shapely polygon
        lane_polygon = Polygon(polygon_points)
        
        violations = 0
        min_distance = float('inf')
        
        for car_point in car_path:
            point = Point(car_point)
            if not lane_polygon.contains(point) and not lane_polygon.touches(point):
                violations += 1
            
            # Calculate minimum distance to boundary
            distance = lane_polygon.boundary.distance(point)
            min_distance = min(min_distance, distance)
        
        in_lane = violations == 0
        result = {
            "result": in_lane,
            "method": "geometric",
            "violations": violations,
            "total_points": len(car_path),
            "min_distance_to_boundary": min_distance if min_distance != float('inf') else 0.0
        }
        return result if return_details else in_lane
        
    except Exception as e:
        # Fallback to interpolation method
        result = _analyze_interpolation(lane_left, lane_right, car_path, return_details)
        if return_details:
            result["method"] = "geometric_fallback_to_interpolation"
            result["fallback_reason"] = str(e)
        return result


def _analyze_interpolation(lane_left, lane_right, car_path, return_details=False):
    """
    Interpolation analysis using SciPy spline interpolation.
    More precise but may fail with insufficient data points.
    """
    # Convert to numpy arrays for easier manipulation
    lane_left_arr = np.array(lane_left)
    lane_right_arr = np.array(lane_right)
    car_path_arr = np.array(car_path)
    
    # Get y-coordinates for interpolation
    left_y = lane_left_arr[:, 1]
    left_x = lane_left_arr[:, 0]
    right_y = lane_right_arr[:, 1]
    right_x = lane_right_arr[:, 0]
    car_y = car_path_arr[:, 1]
    car_x = car_path_arr[:, 0]
    
    # Find the y-range that all three paths cover
    min_y = max(min(left_y), min(right_y), min(car_y))
    max_y = min(max(left_y), max(right_y), max(car_y))
    
    if min_y >= max_y:
        result = {"result": False, "method": "interpolation", "reason": "No overlapping Y range"}
        return result if return_details else False
    
    # Create interpolation functions for lane boundaries
    # Sort by y-coordinate to ensure monotonic interpolation
    left_sorted_idx = np.argsort(left_y)
    right_sorted_idx = np.argsort(right_y)
    
    try:
        # Interpolate x-coordinates as functions of y
        left_interp = interp1d(left_y[left_sorted_idx], left_x[left_sorted_idx], 
                              kind='linear', bounds_error=True)
        right_interp = interp1d(right_y[right_sorted_idx], right_x[right_sorted_idx], 
                               kind='linear', bounds_error=True)
        
        violations = 0
        min_distance = float('inf')
        
        # Check each point in the car path
        for x, y in car_path:
            # Skip points outside the y-range
            if y < min_y or y > max_y:
                continue
                
            # Get the lane boundaries at this y-coordinate
            left_x_at_y = float(left_interp(y))
            right_x_at_y = float(right_interp(y))
            
            # Ensure left is actually to the left of right
            if left_x_at_y > right_x_at_y:
                left_x_at_y, right_x_at_y = right_x_at_y, left_x_at_y
            
            # Check if car is between the lane boundaries
            if x < left_x_at_y or x > right_x_at_y:
                violations += 1
            
            # Calculate minimum distance to boundaries
            distance = min(abs(x - left_x_at_y), abs(x - right_x_at_y))
            min_distance = min(min_distance, distance)
        
        in_lane = violations == 0
        result = {
            "result": in_lane,
            "method": "interpolation",
            "violations": violations,
            "total_points": len(car_path),
            "min_distance_to_boundary": min_distance if min_distance != float('inf') else 0.0
        }
        return result if return_details else in_lane
        
    except Exception as e:
        # Fallback to simple point-by-point comparison if interpolation fails
        return _analyze_point_by_point(lane_left, lane_right, car_path, return_details, str(e))


def _analyze_point_by_point(lane_left, lane_right, car_path, return_details=False, fallback_reason=""):
    """
    Simple point-by-point comparison fallback method.
    Most robust but least precise.
    """
    violations = 0
    min_distance = float('inf')
    
    for car_point in car_path:
        car_x, car_y = car_point
        
        # Find closest points in lane boundaries based on y-coordinate
        left_distances = [abs(ly - car_y) for _, ly in lane_left]
        right_distances = [abs(ry - car_y) for _, ry in lane_right]
        
        closest_left_idx = left_distances.index(min(left_distances))
        closest_right_idx = right_distances.index(min(right_distances))
        
        left_x_boundary = lane_left[closest_left_idx][0]
        right_x_boundary = lane_right[closest_right_idx][0]
        
        # Ensure left is actually to the left of right
        if left_x_boundary > right_x_boundary:
            left_x_boundary, right_x_boundary = right_x_boundary, left_x_boundary
        
        # Check if car is between the boundaries
        if car_x < left_x_boundary or car_x > right_x_boundary:
            violations += 1
        
        # Calculate minimum distance to boundaries
        distance = min(abs(car_x - left_x_boundary), abs(car_x - right_x_boundary))
        min_distance = min(min_distance, distance)
    
    in_lane = violations == 0
    result = {
        "result": in_lane,
        "method": "point_by_point_fallback",
        "violations": violations,
        "total_points": len(car_path),
        "min_distance_to_boundary": min_distance if min_distance != float('inf') else 0.0
    }
    
    if fallback_reason:
        result["fallback_reason"] = fallback_reason
    
    return result if return_details else in_lane


def _analyze_hybrid(lane_left, lane_right, car_path, return_details=False):
    """
    Hybrid analysis combining geometric and interpolation methods.
    Uses the most appropriate method based on data characteristics.
    """
    # Try geometric method first for speed - always get detailed results
    geometric_result = _analyze_geometric(lane_left, lane_right, car_path, True)
    
    # Try interpolation method for precision - always get detailed results
    interpolation_result = _analyze_interpolation(lane_left, lane_right, car_path, True)
    
    # Ensure we have dictionary results
    if not isinstance(geometric_result, dict):
        geometric_result = {"result": geometric_result, "method": "geometric", "violations": 0, "total_points": len(car_path), "min_distance_to_boundary": 0.0}
    if not isinstance(interpolation_result, dict):
        interpolation_result = {"result": interpolation_result, "method": "interpolation", "violations": 0, "total_points": len(car_path), "min_distance_to_boundary": 0.0}
    
    # Compare results and choose the most reliable
    methods_agree = geometric_result["result"] == interpolation_result["result"]
    
    if methods_agree:
        # Both methods agree - use geometric for speed but include interpolation precision
        result = {
            "result": geometric_result["result"],
            "method": "hybrid_consensus",
            "violations": min(geometric_result.get("violations", 0), interpolation_result.get("violations", 0)),
            "total_points": len(car_path),
            "min_distance_to_boundary": max(
                geometric_result.get("min_distance_to_boundary", 0.0),
                interpolation_result.get("min_distance_to_boundary", 0.0)
            ),
            "geometric_result": geometric_result["result"],
            "interpolation_result": interpolation_result["result"],
            "consensus": True
        }
    else:
        # Methods disagree - use more conservative (stricter) result
        stricter_result = geometric_result if not geometric_result["result"] else interpolation_result
        result = {
            "result": stricter_result["result"],
            "method": "hybrid_conservative",
            "violations": max(geometric_result.get("violations", 0), interpolation_result.get("violations", 0)),
            "total_points": len(car_path),
            "min_distance_to_boundary": min(
                geometric_result.get("min_distance_to_boundary", 0.0),
                interpolation_result.get("min_distance_to_boundary", 0.0)
            ),
            "geometric_result": geometric_result["result"],
            "interpolation_result": interpolation_result["result"],
            "consensus": False,
            "chosen_method": stricter_result.get("method", "unknown")
        }
    
    return result if return_details else result["result"] 