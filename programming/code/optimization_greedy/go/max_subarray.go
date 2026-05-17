// go run max_subarray.go 

package main

import (
	"fmt"
)


func maxSubArray(nums []int) int {
    if(len(nums) == 1) {
        return nums[0]
    }

    maxSum := nums[0]

    curMaxSum := 0

    for i:=0; i<len(nums); i++ {
        curMaxSum = max(curMaxSum + nums[i], nums[i])

        maxSum = max(maxSum, curMaxSum)
    }
    
    return maxSum
}


/*
Given an integer array nums, find the subarray with the largest sum, and return its sum.

 

Example 1:

Input: nums = [-2,1,-3,4,-1,2,1,-5,4]
Output: 6
Explanation: The subarray [4,-1,2,1] has the largest sum 6.
Example 2:

Input: nums = [1]
Output: 1
Explanation: The subarray [1] has the largest sum 1.
Example 3:

Input: nums = [5,4,-1,7,8]
Output: 23
Explanation: The subarray [5,4,-1,7,8] has the largest sum 23.

*/

func main() {
	// Define a struct to hold our test cases
	tests := []struct {
		name     string
		input    []int
		expected int
	}{
		{
			name:     "Standard mixed numbers",
			input:    []int{-2, 1, -3, 4, -1, 2, 1, -5, 4},
			expected: 6, // Subarray: [4, -1, 2, 1]
		},
		{
			name:     "Single element positive",
			input:    []int{1},
			expected: 1,
		},
		{
			name:     "Single element negative",
			input:    []int{-5},
			expected: -5,
		},
		{
			name:     "All positive numbers",
			input:    []int{5, 4, -1, 7, 8},
			expected: 23, // Subarray: [5, 4, -1, 7, 8]
		},
		{
			name:     "All negative numbers",
			input:    []int{-2, -3, -1, -5},
			expected: -1, // Subarray: [-1]
		},
	}

	fmt.Println("--- Running Max Subarray Tests ---")
	
	passed := 0
	for _, tc := range tests {
		result := maxSubArray(tc.input)
		if result == tc.expected {
			fmt.Printf("✅ PASS: %s\n   Input: %v -> Expected: %d, Got: %d\n\n", tc.name, tc.input, tc.expected, result)
			passed++
		} else {
			fmt.Printf("❌ FAIL: %s\n   Input: %v -> Expected: %d, Got: %d\n\n", tc.name, tc.input, tc.expected, result)
		}
	}

	fmt.Printf("Result: %d/%d tests passed.\n", passed, len(tests))
}

