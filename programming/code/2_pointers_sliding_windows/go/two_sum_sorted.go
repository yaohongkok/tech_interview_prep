// How to run:
// go run two_sum_sorted.go

package main

import "fmt"

func twoSum(numbers []int, target int) []int {
    numbersLen := len(numbers)
    idx1 := 0
    idx2 := numbersLen - 1

    currentTotal := numbers[idx1] + numbers[idx2]

	// edge case: if the sum of the first and last 
	// element is already equal to target, 
	// then we can return immediately.
	// Or it could cause return empty
    if currentTotal == target {
        return []int{idx1+1, idx2+1}
    }

	// as long as idx1 < idx2 - 1 
	// idx2- 1 because if idx1 cannot equal to idx2
    for (idx1 < (idx2 -1)) {
		// when total > target, lower right pointer
        if(currentTotal > target) {
            idx2--
        }

		// when total < target, raise left pointer
        if(currentTotal < target) {
            idx1++
        }

        currentTotal = numbers[idx1] + numbers[idx2]

        if currentTotal == target {
            return []int{idx1+1, idx2+1}
        }
    }

    return nil

}


// Given a 1-indexed array of integers numbers that is already sorted in non-decreasing order, 
// find two numbers such that they add up to a specific target number. 
// Let these two numbers be numbers[index1] and numbers[index2] where 
// 1 <= index1 < index2 <= numbers.length.
// Return the indices of the two numbers index1 and index2, 
// each incremented by one, as an integer array [index1, index2] of length 2.

// The tests are generated such that there is exactly one solution. You may not use the same element twice.

// Your solution must use only constant extra space.


// Example 1:

// Input: numbers = [2,7,11,15], target = 9
// Output: [1,2]
// Explanation: The sum of 2 and 7 is 9. Therefore, index1 = 1, index2 = 2. We return [1, 2].

// Example 2:

// Input: numbers = [2,3,4], target = 6
// Output: [1,3]
// Explanation: The sum of 2 and 4 is 6. Therefore index1 = 1, index2 = 3. We return [1, 3].

// Example 3:

// Input: numbers = [-1,0], target = -1
// Output: [1,2]
// Explanation: The sum of -1 and 0 is -1. Therefore index1 = 1, index2 = 2. We return [1, 2].


func main() {
	// Test Case 1: Standard case
	nums1 := []int{2, 7, 11, 15}
	target1 := 9
	fmt.Printf("Test 1: nums=%v, target=%d -> Result: %v\n", nums1, target1, twoSum(nums1, target1))

	// Test Case 2: Target is at the very ends (your specific edge case)
	nums2 := []int{1, 3, 4, 5, 8}
	target2 := 9
	fmt.Printf("Test 2: nums=%v, target=%d -> Result: %v\n", nums2, target2, twoSum(nums2, target2))

	// Test Case 3: Target in the middle
	nums3 := []int{5, 25, 75, 100}
	target3 := 100
	fmt.Printf("Test 3: nums=%v, target=%d -> Result: %v\n", nums3, target3, twoSum(nums3, target3))

	// Test Case 4: No solution
	nums4 := []int{1, 2, 3}
	target4 := 10
	fmt.Printf("Test 4: nums=%v, target=%d -> Result: %v\n", nums4, target4, twoSum(nums4, target4))
}



