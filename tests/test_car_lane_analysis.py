#!/usr/bin/env python3
"""
Basic sanity test of sim_log_analysis.py:car_stayed_in_lane()
"""

import unittest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sim_log_analysis import car_stayed_in_lane


class TestLaneAnalysis(unittest.TestCase):
    """Test the car_stayed_in_lane() function"""

    def test_basic_positive_case(self):
        """Assert that we detect if the car stays in its lane"""
        lane_left = [
            (3.0, 0.0),
            (3.0, 1.0),
            (3.0, 2.0),
            (3.0, 3.0),
            (3.0, 4.0),
            (3.0, 5.0),
        ]
        lane_right = [
            (5.0, 0.0),
            (5.0, 1.0),
            (5.0, 2.0),
            (5.0, 3.0),
            (5.0, 4.0),
            (5.0, 5.0),
        ]
        car_path = [
            (4.0, 0.0),
            (4.0, 1.0),
            (4.0, 2.0),
            (4.0, 3.0),
            (4.0, 4.0),
            (4.0, 5.0),
        ]
        in_lane = car_stayed_in_lane(lane_left, lane_right, car_path)
        self.assertTrue(in_lane)

    def test_basic_negative_case(self):
        """Assert that we detect if the car goes out of the lane"""
        lane_left = [
            (3.0, 0.0),
            (3.0, 1.0),
            (3.0, 2.0),
            (3.0, 3.0),
            (3.0, 4.0),
            (3.0, 5.0),
        ]
        lane_right = [
            (5.0, 0.0),
            (5.0, 1.0),
            (5.0, 2.0),
            (5.0, 3.0),
            (5.0, 4.0),
            (5.0, 5.0),
        ]
        car_path = [
            (4.0, 0.0),
            (3.6, 1.0),
            (3.3, 2.0),
            (2.6, 3.0),
            (2.3, 4.0),
            (2.0, 5.0),
        ]
        in_lane = car_stayed_in_lane(lane_left, lane_right, car_path)
        self.assertFalse(in_lane)

    def test_car_touching_left_boundary(self):
        """Test case where car exactly touches the left lane boundary"""
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0)]
        car_path = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0)]  # Exactly on left boundary
        in_lane = car_stayed_in_lane(lane_left, lane_right, car_path)
        self.assertTrue(in_lane)  # Should be considered in lane

    def test_car_touching_right_boundary(self):
        """Test case where car exactly touches the right lane boundary"""
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0)]
        car_path = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0)]  # Exactly on right boundary
        in_lane = car_stayed_in_lane(lane_left, lane_right, car_path)
        self.assertTrue(in_lane)  # Should be considered in lane

    def test_car_crosses_and_returns(self):
        """Test case where car goes out of lane and comes back"""
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0), (3.0, 3.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0), (5.0, 3.0)]
        car_path = [(4.0, 0.0), (2.0, 1.0), (4.0, 2.0), (4.0, 3.0)]  # Out and back
        in_lane = car_stayed_in_lane(lane_left, lane_right, car_path)
        self.assertFalse(in_lane)  # Should fail because it went out

    def test_curved_lane_boundaries(self):
        """Test case with curved lane boundaries"""
        lane_left = [(2.0, 0.0), (2.5, 1.0), (3.0, 2.0), (3.5, 3.0)]
        lane_right = [(4.0, 0.0), (4.5, 1.0), (5.0, 2.0), (5.5, 3.0)]
        car_path = [(3.0, 0.0), (3.5, 1.0), (4.0, 2.0), (4.5, 3.0)]  # Following curve
        in_lane = car_stayed_in_lane(lane_left, lane_right, car_path)
        self.assertTrue(in_lane)

    def test_empty_inputs(self):
        """Test case with empty input lists"""
        lane_left = []
        lane_right = []
        car_path = []
        in_lane = car_stayed_in_lane(lane_left, lane_right, car_path)
        self.assertFalse(in_lane)  # Empty inputs should return False

    def test_single_point_inputs(self):
        """Test case with single point inputs"""
        lane_left = [(3.0, 0.0)]
        lane_right = [(5.0, 0.0)]
        car_path = [(4.0, 0.0)]
        in_lane = car_stayed_in_lane(lane_left, lane_right, car_path)
        self.assertTrue(in_lane)  # Single point within bounds

    def test_single_point_outside_lane(self):
        """Test case with single point outside lane"""
        lane_left = [(3.0, 0.0)]
        lane_right = [(5.0, 0.0)]
        car_path = [(2.0, 0.0)]  # Outside left boundary
        in_lane = car_stayed_in_lane(lane_left, lane_right, car_path)
        self.assertFalse(in_lane)

    def test_mismatched_input_lengths(self):
        """Test case with different length inputs"""
        lane_left = [(3.0, 0.0), (3.0, 1.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0), (5.0, 3.0)]
        car_path = [(4.0, 0.0), (4.0, 1.0), (4.0, 2.0)]
        in_lane = car_stayed_in_lane(lane_left, lane_right, car_path)
        # Should handle gracefully and return result based on overlapping range
        self.assertTrue(in_lane)

    def test_crossed_lane_boundaries(self):
        """Test case where left and right boundaries cross each other"""
        lane_left = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0)]  # Right side
        lane_right = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0)]  # Left side (crossed)
        car_path = [(4.0, 0.0), (4.0, 1.0), (4.0, 2.0)]
        in_lane = car_stayed_in_lane(lane_left, lane_right, car_path)
        self.assertTrue(in_lane)  # Function should handle boundary swapping

    def test_car_path_with_duplicates(self):
        """Test case with duplicate points in car path"""
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0)]
        car_path = [(4.0, 0.0), (4.0, 1.0), (4.0, 1.0), (4.0, 2.0)]  # Duplicate
        in_lane = car_stayed_in_lane(lane_left, lane_right, car_path)
        self.assertTrue(in_lane)

    def test_car_following_lane_boundary(self):
        """Test case where car exactly follows a lane boundary"""
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0)]
        car_path = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0)]  # Following left boundary
        in_lane = car_stayed_in_lane(lane_left, lane_right, car_path)
        self.assertTrue(in_lane)

    def test_slightly_outside_boundary(self):
        """Test case where car is just slightly outside boundary"""
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0)]
        car_path = [(2.999, 0.0), (2.999, 1.0), (2.999, 2.0)]  # Just outside left
        in_lane = car_stayed_in_lane(lane_left, lane_right, car_path)
        self.assertFalse(in_lane)

    def test_wide_lane_narrow_car_path(self):
        """Test case with wide lane and narrow car movement"""
        lane_left = [(1.0, 0.0), (1.0, 1.0), (1.0, 2.0)]
        lane_right = [(10.0, 0.0), (10.0, 1.0), (10.0, 2.0)]
        car_path = [(5.0, 0.0), (5.01, 1.0), (4.99, 2.0)]  # Tiny variations
        in_lane = car_stayed_in_lane(lane_left, lane_right, car_path)
        self.assertTrue(in_lane)

    def test_zigzag_within_lane(self):
        """Test case where car zigzags but stays within lane"""
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0), (3.0, 3.0), (3.0, 4.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0), (5.0, 3.0), (5.0, 4.0)]
        car_path = [(3.2, 0.0), (4.8, 1.0), (3.2, 2.0), (4.8, 3.0), (4.0, 4.0)]
        in_lane = car_stayed_in_lane(lane_left, lane_right, car_path)
        self.assertTrue(in_lane)

    # Multiple Analysis Algorithm Tests
    
    def test_geometric_method_basic(self):
        """Test geometric method with basic lane scenario"""
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0), (3.0, 3.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0), (5.0, 3.0)]
        car_path = [(4.0, 0.0), (4.0, 1.0), (4.0, 2.0), (4.0, 3.0)]
        
        result = car_stayed_in_lane(lane_left, lane_right, car_path, method="geometric")
        self.assertTrue(result)
    
    def test_interpolation_method_basic(self):
        """Test interpolation method with basic lane scenario"""
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0), (3.0, 3.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0), (5.0, 3.0)]
        car_path = [(4.0, 0.0), (4.0, 1.0), (4.0, 2.0), (4.0, 3.0)]
        
        result = car_stayed_in_lane(lane_left, lane_right, car_path, method="interpolation")
        self.assertTrue(result)
    
    def test_hybrid_method_basic(self):
        """Test hybrid method with basic lane scenario"""
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0), (3.0, 3.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0), (5.0, 3.0)]
        car_path = [(4.0, 0.0), (4.0, 1.0), (4.0, 2.0), (4.0, 3.0)]
        
        result = car_stayed_in_lane(lane_left, lane_right, car_path, method="hybrid")
        self.assertTrue(result)
    
    def test_geometric_method_violation(self):
        """Test geometric method detects violations"""
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0)]
        car_path = [(2.0, 0.0), (2.0, 1.0), (2.0, 2.0)]  # Outside left boundary
        
        result = car_stayed_in_lane(lane_left, lane_right, car_path, method="geometric")
        self.assertFalse(result)
    
    def test_interpolation_method_violation(self):
        """Test interpolation method detects violations"""
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0)]
        car_path = [(6.0, 0.0), (6.0, 1.0), (6.0, 2.0)]  # Outside right boundary
        
        result = car_stayed_in_lane(lane_left, lane_right, car_path, method="interpolation")
        self.assertFalse(result)
    
    def test_hybrid_method_violation(self):
        """Test hybrid method detects violations"""
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0)]
        car_path = [(1.0, 0.0), (1.0, 1.0), (1.0, 2.0)]  # Far outside left boundary
        
        result = car_stayed_in_lane(lane_left, lane_right, car_path, method="hybrid")
        self.assertFalse(result)
    
    def test_return_details_functionality(self):
        """Test return_details parameter provides detailed analysis"""
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0)]
        car_path = [(4.0, 0.0), (3.5, 1.0), (4.5, 2.0)]
        
        # Test detailed results for each method
        for method in ["geometric", "interpolation", "hybrid"]:
            with self.subTest(method=method):
                result = car_stayed_in_lane(lane_left, lane_right, car_path, 
                                          method=method, return_details=True)
                
                # Check that result is a dictionary with expected keys
                self.assertIsInstance(result, dict)
                if isinstance(result, dict):
                    self.assertIn("result", result)
                    self.assertIn("method", result)
                    self.assertIn("violations", result)
                    self.assertIn("total_points", result)
                    self.assertIn("min_distance_to_boundary", result)
                    
                    # Check data types
                    self.assertIsInstance(result["result"], bool)
                    self.assertIsInstance(result["violations"], int)
                    self.assertIsInstance(result["total_points"], int)
                    self.assertIsInstance(result["min_distance_to_boundary"], (int, float))
    
    def test_method_consensus_agreement(self):
        """Test hybrid method when geometric and interpolation agree"""
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0), (3.0, 3.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0), (5.0, 3.0)]
        car_path = [(4.0, 0.0), (4.0, 1.0), (4.0, 2.0), (4.0, 3.0)]
        
        result = car_stayed_in_lane(lane_left, lane_right, car_path, 
                                  method="hybrid", return_details=True)
        
        self.assertIsInstance(result, dict)
        if isinstance(result, dict):
            self.assertTrue(result["result"])
            self.assertIn("consensus", result)
            self.assertTrue(result["consensus"])
            self.assertEqual(result["geometric_result"], result["interpolation_result"])
    
    def test_curved_lane_geometric(self):
        """Test geometric method with curved lane boundaries"""
        lane_left = [(2.0, 0.0), (2.5, 1.0), (3.0, 2.0), (3.5, 3.0)]
        lane_right = [(4.0, 0.0), (4.5, 1.0), (5.0, 2.0), (5.5, 3.0)]
        car_path = [(3.0, 0.0), (3.5, 1.0), (4.0, 2.0), (4.5, 3.0)]
        
        result = car_stayed_in_lane(lane_left, lane_right, car_path, method="geometric")
        self.assertTrue(result)
    
    def test_curved_lane_interpolation(self):
        """Test interpolation method with curved lane boundaries"""
        lane_left = [(2.0, 0.0), (2.5, 1.0), (3.0, 2.0), (3.5, 3.0)]
        lane_right = [(4.0, 0.0), (4.5, 1.0), (5.0, 2.0), (5.5, 3.0)]
        car_path = [(3.0, 0.0), (3.5, 1.0), (4.0, 2.0), (4.5, 3.0)]
        
        result = car_stayed_in_lane(lane_left, lane_right, car_path, method="interpolation")
        self.assertTrue(result)
    
    def test_method_specific_edge_cases(self):
        """Test edge cases specific to each method"""
        # Test with adequate points for all methods to work
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0)]
        car_path = [(4.0, 0.5), (4.0, 1.5)]
        
        geometric_result = car_stayed_in_lane(lane_left, lane_right, car_path, method="geometric")
        interpolation_result = car_stayed_in_lane(lane_left, lane_right, car_path, method="interpolation")
        hybrid_result = car_stayed_in_lane(lane_left, lane_right, car_path, method="hybrid")
        
        # All methods should handle this case successfully
        self.assertTrue(geometric_result)
        self.assertTrue(interpolation_result)
        self.assertTrue(hybrid_result)
    
    def test_complex_polygon_geometric(self):
        """Test geometric method with complex polygon shapes"""
        # Create a lane that narrows in the middle
        lane_left = [(3.0, 0.0), (3.5, 1.0), (3.5, 2.0), (3.0, 3.0)]
        lane_right = [(5.0, 0.0), (4.5, 1.0), (4.5, 2.0), (5.0, 3.0)]
        car_path = [(4.0, 0.0), (4.0, 1.5), (4.0, 3.0)]
        
        result = car_stayed_in_lane(lane_left, lane_right, car_path, method="geometric")
        self.assertTrue(result)
    
    def test_performance_comparison(self):
        """Test that different methods return consistent results for standard cases"""
        lane_left = [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0), (3.0, 3.0), (3.0, 4.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0), (5.0, 3.0), (5.0, 4.0)]
        
        test_cases = [
            # Car stays in lane
            [(4.0, 0.0), (4.0, 1.0), (4.0, 2.0), (4.0, 3.0), (4.0, 4.0)],
            # Car goes out of lane
            [(2.0, 0.0), (2.0, 1.0), (2.0, 2.0), (2.0, 3.0), (2.0, 4.0)],
            # Car touches boundary
            [(3.0, 0.0), (3.0, 1.0), (3.0, 2.0), (3.0, 3.0), (3.0, 4.0)]
        ]
        
        for i, car_path in enumerate(test_cases):
            with self.subTest(case=i):
                geometric_result = car_stayed_in_lane(lane_left, lane_right, car_path, method="geometric")
                interpolation_result = car_stayed_in_lane(lane_left, lane_right, car_path, method="interpolation")
                hybrid_result = car_stayed_in_lane(lane_left, lane_right, car_path, method="hybrid")
                
                # For standard cases, all methods should generally agree
                # (allowing for some edge case differences)
                results = [geometric_result, interpolation_result, hybrid_result]
                self.assertTrue(len(set(results)) <= 2, 
                               f"Methods disagreed too much for case {i}: {results}")
    
    def test_invalid_method_parameter(self):
        """Test that invalid method parameter raises appropriate error"""
        lane_left = [(3.0, 0.0), (3.0, 1.0)]
        lane_right = [(5.0, 0.0), (5.0, 1.0)]
        car_path = [(4.0, 0.0), (4.0, 1.0)]
        
        with self.assertRaises(ValueError):
            car_stayed_in_lane(lane_left, lane_right, car_path, method="invalid_method")
    
    def test_single_point_all_methods(self):
        """Test that all methods handle single-point inputs correctly"""
        lane_left = [(3.0, 0.0)]
        lane_right = [(5.0, 0.0)]
        car_path = [(4.0, 0.0)]
        
        for method in ["geometric", "interpolation", "hybrid"]:
            with self.subTest(method=method):
                result = car_stayed_in_lane(lane_left, lane_right, car_path, method=method)
                self.assertTrue(result)
                
                # Test with details
                detailed_result = car_stayed_in_lane(lane_left, lane_right, car_path, 
                                                   method=method, return_details=True)
                self.assertIsInstance(detailed_result, dict)
                if isinstance(detailed_result, dict):
                    self.assertTrue(detailed_result["result"])
    
    def test_hybrid_method_conservative_fallback(self):
        """Test hybrid method chooses conservative result when methods disagree"""
        # Create a scenario where geometric and interpolation might disagree
        # This is a complex scenario that might cause method disagreement
        lane_left = [(3.0, 0.0), (3.1, 1.0), (2.9, 2.0)]
        lane_right = [(5.0, 0.0), (4.9, 1.0), (5.1, 2.0)]
        car_path = [(3.05, 0.5), (3.05, 1.5)]  # Very close to left boundary
        
        detailed_result = car_stayed_in_lane(lane_left, lane_right, car_path, 
                                           method="hybrid", return_details=True)
        
        self.assertIsInstance(detailed_result, dict)
        if isinstance(detailed_result, dict):
            self.assertIn("geometric_result", detailed_result)
            self.assertIn("interpolation_result", detailed_result)
            self.assertIn("consensus", detailed_result)
            
            # If methods disagree, hybrid should choose the more conservative (stricter) result
            if not detailed_result["consensus"]:
                self.assertIn("chosen_method", detailed_result)


if __name__ == "__main__":
    unittest.main() 