package meetings

import "testing"

func TestMinMeetingRooms(t *testing.T) {
	tests := []struct {
		name     string
		start    []int
		end      []int
		expected int
	}{
		{
			name:     "Example 1: No overlaps",
			start:    []int{1, 10, 7},
			end:      []int{4, 15, 10},
			expected: 1,
		},
		{
			name:     "Example 2: Overlapping meetings",
			start:    []int{2, 9, 6},
			end:      []int{4, 12, 10},
			expected: 2,
		},
		{
			name:     "All meetings at the same time",
			start:    []int{5, 5, 5},
			end:      []int{10, 10, 10},
			expected: 3,
		},
		{
			name:     "Back-to-back meetings (Should reuse room)",
			start:    []int{1, 5, 10},
			end:      []int{5, 10, 15},
			expected: 1,
		},
		{
			name:     "Empty input",
			start:    []int{},
			end:      []int{},
			expected: 0,
		},
		{
			name:     "Single meeting",
			start:    []int{1},
			end:      []int{5},
			expected: 1,
		},
		{
			name:     "Nested meetings",
			start:    []int{1, 2, 3},
			end:      []int{10, 9, 8},
			expected: 3,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := MinMeetingRooms(tt.start, tt.end)
			if result != tt.expected {
				t.Errorf("MinMeetingRooms() = %d; want %d", result, tt.expected)
			}
		})
	}
}