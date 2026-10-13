// How to run:
// go run is_subsequence.go

package main

import "fmt"


func isSubsequence(s string, t string) bool {
    s_len := len(s)

	// edge condition: empty string is a subsequence of any string
    if(s_len == 0) {
        return true;
    }

    s_idx := 0;
    s_char := s[s_idx]

    for t_idx:= 0; t_idx < len(t); t_idx++ {
        t_char := t[t_idx]

        if(s_char == t_char) {
			// move pointer to the next character in s
			// but check that we are not at the end
			// if at the end, then we have found all characters in s in t, so return true
            s_idx++

            if(s_idx >= s_len) {
                return true
            } else {
                s_char = s[s_idx]
            }
        }
    }

    return false;
}




// Given two strings s and t, return true if s is a 
// subsequence of t, or false otherwise.

// A subsequence of a string is a new string that is 
// formed from the original string by deleting some 
// (can be none) of the characters without disturbing 
// the relative positions of the remaining characters. 
// (i.e., "ace" is a subsequence of "abcde" while "aec" 
// is not).


// Example 1:

// Input: s = "abc", t = "ahbgdc"
// Output: true
// Example 2:

// Input: s = "axc", t = "ahbgdc"
// Output: false


func main() {
    // Define test cases: {s, t, expected_result}
    tests := []struct {
        s        string
        t        string
        expected bool
    }{
        {"abc", "ahbgdc", true},    // Standard positive case
        {"axc", "ahbgdc", false},   // Character 'x' is missing
        {"", "ahbgdc", true},       // Empty s is always true
        {"abc", "", false},         // Empty t is false unless s is also empty
        {"aaaaaa", "bbaaaa", false}, // Not enough 'a's in t
        {"ab", "ba", false},        // Characters exist but in wrong order
    }

    fmt.Printf("%-10s | %-15s | %-8s | %-8s\n", "s", "t", "Result", "Status")
    fmt.Println("----------------------------------------------------------")

    for _, tc := range tests {
        result := isSubsequence(tc.s, tc.t)
        status := "PASS"
        if result != tc.expected {
            status = "FAIL"
        }
        
        fmt.Printf("%-10q | %-15q | %-8t | %-8s\n", tc.s, tc.t, result, status)
    }
}
