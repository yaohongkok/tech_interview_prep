package main

import "fmt"


type Window struct {
	counts         map[int]int
	violationCount int // Number of unique elements appearing > 1 time
	currentSum     int64
}

func maximumSubarraySum(nums []int, k int) int64 {
	var maxSubarraySum int64 = 0
	
	// Pre-allocate map to size k to prevent memory re-allocations
	w := &Window{
		counts: make(map[int]int, k),
	}

	for i, val := range nums {
		// Add the element entering from the right
		w.addElement(val)

		// Once the window exceeds size k, remove the element falling off the left
		if i >= k {
			w.removeElement(nums[i-k])
		}

		// Check if the current window is full (size k) and valid (no violations)
		if i >= k-1 && w.isValid() {
			if w.currentSum > maxSubarraySum {
				maxSubarraySum = w.currentSum
			}
		}
	}

	return maxSubarraySum
}

// addElement handles the logic for a number entering the window
func (w *Window) addElement(val int) {
	w.currentSum += int64(val)
	w.counts[val]++
	
	// If this is the second time we've seen this number, 
	// it's a new violation.
	if w.counts[val] == 2 {
		w.violationCount++
	}
}

// removeElement handles the logic for a number leaving the window
func (w *Window) removeElement(val int) {
	w.currentSum -= int64(val)
	
	// If the count was 2, it's about to become 1. 
	// This number is no longer a violation.
	if w.counts[val] == 2 {
		w.violationCount--
	}
	
	w.counts[val]--
	if w.counts[val] == 0 {
		delete(w.counts, val)
	}
}

// isValid returns true if every number in the window is unique
func (w *Window) isValid() bool {
	return w.violationCount == 0
}



// You are given an integer array nums and an integer k. Find the maximum subarray sum of all the subarrays of nums that meet the following conditions:

// The length of the subarray is k, and
// All the elements of the subarray are distinct.
// Return the maximum subarray sum of all the subarrays that meet the conditions. If no subarray meets the conditions, return 0.

// A subarray is a contiguous non-empty sequence of elements within an array.

 

// Example 1:

// Input: nums = [1,5,4,2,9,9,9], k = 3
// Output: 15
// Explanation: The subarrays of nums with length 3 are:
// - [1,5,4] which meets the requirements and has a sum of 10.
// - [5,4,2] which meets the requirements and has a sum of 11.
// - [4,2,9] which meets the requirements and has a sum of 15.
// - [2,9,9] which does not meet the requirements because the element 9 is repeated.
// - [9,9,9] which does not meet the requirements because the element 9 is repeated.
// We return 15 because it is the maximum subarray sum of all the subarrays that meet the conditions
// Example 2:

// Input: nums = [4,4,4], k = 3
// Output: 0
// Explanation: The subarrays of nums with length 3 are:
// - [4,4,4] which does not meet the requirements because the element 4 is repeated.
// We return 0 because no subarrays meet the conditions.



func main() {
	// Define a slice of test cases
	testCases := []struct {
		name     string
		nums     []int
		k        int
		expected int64
	}{
		{
			name:     "Standard case with duplicates",
			nums:     []int{1, 5, 4, 2, 9, 9, 9},
			k:        3,
			expected: 15, // [5, 4, 2] = 11, [4, 2, 9] = 15. [2, 9, 9] is invalid.
		},
		{
			name:     "Five identical numbers (The '1's streak)",
			nums:     []int{1, 1, 1, 1, 1},
			k:        3,
			expected: 0, // No valid subarray of unique elements
		},
		{
			name:     "All unique elements",
			nums:     []int{1, 2, 3, 4, 5},
			k:        2,
			expected: 9, // [4, 5]
		},
		{
			name:     "k equals array length (Valid)",
			nums:     []int{1, 2, 3},
			k:        3,
			expected: 6,
		},
		{
			name:     "k equals array length (Invalid due to duplicates)",
			nums:     []int{1, 2, 1},
			k:        3,
			expected: 0,
		},
		{
			name:     "Alternating duplicates",
			nums:     []int{1, 2, 1, 2, 1, 2},
			k:        2,
			expected: 3, // [1, 2] or [2, 1]
		},
		{
			name:     "Large k compared to array",
			nums:     []int{1, 2},
			k:        5,
			expected: 0, // Window can never be formed
		},
		{
			name:     "Minimum k size",
			nums:     []int{1, 2, 3},
			k:        1,
			expected: 3, // Max single element is 3
		},
	}

	fmt.Printf("%-45s | %-10s | %-10s\n", "Test Case Name", "Result", "Status")
	fmt.Println("--------------------------------------------------------------------------------")

	for _, tc := range testCases {
		result := maximumSubarraySum(tc.nums, tc.k)
		status := "❌ FAIL"
		if result == tc.expected {
			status = "✅ PASS"
		}
		fmt.Printf("%-45s | %-10d | %-10s\n", tc.name, result, status)
	}
}





// --------------------------------------------



func maximumSubarraySum_scalable(nums []int, k int) int64 {
    var maxSum int64 = 0

    numsSeenCountMap := make(map[int64]int)
    var curSum int64 = 0

    repeatedNum := 0

    for i := 0; i < len(nums)-k+1; i++ {

        if i > 0 {
            curLeftVal := int64(nums[i-1])
            curSum = curSum - curLeftVal

            numsSeenCountMap[curLeftVal]--

            if(numsSeenCountMap[curLeftVal] == 0) {
                delete(numsSeenCountMap, curLeftVal)
            } else if(numsSeenCountMap[curLeftVal] > 0) {
                repeatedNum--
            }

            curRightVal := int64(nums[i+k-1])
            curSum = curSum + curRightVal

            if _,ok := numsSeenCountMap[curRightVal]; !ok {
                numsSeenCountMap[curRightVal] = 1
            } else {
                numsSeenCountMap[curRightVal] ++
                repeatedNum++
            }
        } else {
            // Running for first time, i =0
            for j := 0; j < k; j++ {
				fmt.Printf("k: %d\n", k)
				fmt.Printf("i: %d, j: %d\n", i, j)

                curVal := int64(nums[j])
                curSum = curSum + curVal

                if _,ok := numsSeenCountMap[curVal]; !ok {
                    numsSeenCountMap[curVal] = 1
                } else {
                    numsSeenCountMap[curVal] ++
                    repeatedNum++
                }
            }
        }

        fmt.Printf("curSum: %d\n", curSum)
        fmt.Printf("repeatedNum: %d\n", repeatedNum)

        if repeatedNum == 0 && curSum > maxSum {
            maxSum = curSum
        }
    }

    return maxSum
}


func maximumSubarraySum_lessEfficient(nums []int, k int) int64 {
    var maxSum int64 = 0

    for i := 0; i < len(nums)-k+1; i++ {
        numsSeenMap := make(map[int64]bool)
        isSubArrDistinct := true

        var curSum int64 = 0
        for j := 0; j < k; j++ {
            curVal := int64(nums[i+j])

            if _,ok := numsSeenMap[curVal]; !ok {
                curSum = curSum + curVal
                numsSeenMap[curVal] = true
            } else {
                isSubArrDistinct = false
                break
            }
        }

        if isSubArrDistinct && curSum > maxSum {
            maxSum = curSum
        }
    }

    return maxSum
}