// go run longest_unique_substr.go 

package main

import "fmt"

// Optimized version
func lengthOfLongestSubstring(s string) int {
    charIdxMap := make(map[byte]int)
    longestLen := 0
    leftIdx := 0

    for rightIdx := 0; rightIdx < len(s); rightIdx++ {
        curChar := s[rightIdx]

        // If the character was seen AND is within our current sliding window
		// the condition "prevIdx >= leftIdx" is important to 
		// make sure that we only move leftIdx when 
		// the previous seen index of the current character is 
		// within the current sliding window.
        if prevIdx, ok := charIdxMap[curChar]; ok && prevIdx >= leftIdx {
            leftIdx = prevIdx + 1
        }

        // Update the map with the most recent position
        charIdxMap[curChar] = rightIdx

        // Calculate length and update maximum
        currentWindowLen := rightIdx - leftIdx + 1
        if currentWindowLen > longestLen {
            longestLen = currentWindowLen
        }
    }

    return longestLen
}


func lengthOfLongestSubstring_mine(s string) int {
    if(len(s) <= 1) {
        return len(s)
    }

    longestLen := 0
    // longestUniqueSeq := ""
    charSeen := make(map[byte]int)

    leftIdx := 0
    rightIdx := 0
    var curSeqLen int

    for rightIdx=0; rightIdx < len(s); rightIdx++ {
        curChar := s[rightIdx]

		// the better way to only enter this logic when prevSeenIdx > leftIdx.
		// Then, no need to take care of the map
        if prevSeenIdx, ok := charSeen[curChar]; ok {
			// calculate longest length if there is a 
			// repeating character, and then move leftIdx to the right of the previous seen index of the current character
            curSeqLen = rightIdx - leftIdx
            if(curSeqLen > longestLen) {
                longestLen = curSeqLen
                // longestUniqueSeq = [leftIdx:rightIdx+1]
            }

            newLeftIdx := prevSeenIdx + 1

			// when we move leftIdx one-by-one, we have to 
			// remove them from charSeen as well, 
			// otherwise we will have incorrect prevSeenIdx for 
			// the characters in the current sequence

            for leftIdx < newLeftIdx {
                delete(charSeen, s[leftIdx])
                leftIdx++
            }
            
        }

        charSeen[curChar] = rightIdx
    }

    // Handling the case where there is no repeating character at all or towards the end
    curSeqLen = rightIdx - leftIdx

    if(curSeqLen > longestLen) {
        longestLen = curSeqLen
        // longestUniqueSeq = [leftIdx:rightIdx+1]
    }

    return longestLen
}



// Given a string s, find the length of the longest substring without duplicate characters.

// Example 1:

// Input: s = "abcabcbb"
// Output: 3
// Explanation: The answer is "abc", with the length of 3. Note that "bca" and "cab" are also correct answers.
// Example 2:

// Input: s = "bbbbb"
// Output: 1
// Explanation: The answer is "b", with the length of 1.
// Example 3:

// Input: s = "pwwkew"
// Output: 3
// Explanation: The answer is "wke", with the length of 3.
// Notice that the answer must be a substring, "pwke" is a subsequence and not a substring.


func main() {
	tests := []struct {
		name     string
		input    string
		expected int
	}{
		{"Empty String", "", 0},
		{"Single Character", "a", 1},
		{"All Identical", "bbbbb", 1},
		{"Standard Case", "abcabcbb", 3},
		{"Longest at End", "pwwkew", 3},
		{"Non-Repeating", "abcdefg", 7},
		{"Two-Character Toggle", "abababab", 2},
		{"Internal Jump", "abba", 2},
		{"Special Characters", "a b!@a b!", 5}, // "b!@a " or "!@a b"
		{"Your Example (Middle Cluster)", "abcdddcbaefghijk", 11},
	}

	fmt.Printf("%-25s | %-20s | %-8s | %-8s\n", "Test Name", "Input", "Result", "Status")
	fmt.Println("--------------------------------------------------------------------------------")

	for _, tc := range tests {
		result := lengthOfLongestSubstring(tc.input)
		status := "PASS"
		if result != tc.expected {
			status = "FAIL"
		}
		fmt.Printf("%-25s | %-20s | %-8d | %-8s\n", tc.name, "\""+tc.input+"\"", result, status)
	}
}