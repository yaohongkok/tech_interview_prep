// How to run:
// go run valid_palindrome.go

package main

import (
	"fmt"
	"strings"
)

func isPalindrome(s string) bool {
    s = strings.ToLower(s)
    s = toAlphaNumeric(s)

    headIdx := 0
    tailIdx := len(s) - 1

    for (headIdx < tailIdx) {
        if(s[headIdx] != s[tailIdx]) {
            return false
        }

        headIdx++
        tailIdx--
    }

    return true
}

func toAlphaNumeric(s string) string {
    var alphaNumBuilder strings.Builder

    for i:=0; i < len(s); i++ {
        char := s[i]

        if((char >= 'a' && char <= 'z') || 
          (char >= '0' && char <='9')) {
            alphaNumBuilder.WriteByte(char)
        }
    }

    return alphaNumBuilder.String()
}


// A phrase is a palindrome if, after converting all uppercase 
// letters into lowercase letters and removing all 
// non-alphanumeric characters, it reads the same forward and 
// backward. Alphanumeric characters include letters and numbers.

// Given a string s, return true if it is a palindrome, or 
// false otherwise.

 

// Example 1:

// Input: s = "A man, a plan, a canal: Panama"
// Output: true
// Explanation: "amanaplanacanalpanama" is a palindrome.
// Example 2:

// Input: s = "race a car"
// Output: false
// Explanation: "raceacar" is not a palindrome.
// Example 3:

// Input: s = " "
// Output: true
// Explanation: s is an empty string "" after removing non-alphanumeric characters.
// Since an empty string reads the same forward and backward, it is a palindrome.


func main() {
	// Define test cases: input -> expected output
	testCases := []struct {
		input    string
		expected bool
	}{
		{"A man, a plan, a canal: Panama", true},
		{"race a car", false},
		{" ", true}, // Empty/whitespace usually counts as palindrome
		{"0P", false},
		{"Was it a cat I saw?", true},
		{"No 'x' in Nixon", true},
		{"12321", true},
		{"123456", false},
	}

	fmt.Printf("%-35s | %-10s | %-10s\n", "Input", "Result", "Status")
	fmt.Println(strings.Repeat("-", 60))

	for _, tc := range testCases {
		result := isPalindrome(tc.input)
		status := "❌ FAIL"
		if result == tc.expected {
			status = "✅ PASS"
		}

		fmt.Printf("%-35s | %-10t | %-10s\n", tc.input, result, status)
	}
}
