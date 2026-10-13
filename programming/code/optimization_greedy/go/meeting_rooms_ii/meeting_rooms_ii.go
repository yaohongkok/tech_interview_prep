/*
Key Trick: Create a map of hourly meeting counts and
then find the maximum overlap in the map. This will give us
the minimum number of rooms required to attend all meetings.
*/

package meetings

func MinMeetingRooms(start []int, end []int) int {

	hourlyMeetingCountMap := createMeetingCountMap()

	for i := 0; i < len(start); i++ {
		isMeetingCrossDay := end[i] < start[i]

		currentEnd := end[i]

		if isMeetingCrossDay {
			currentEnd = 24
		}

		for j := start[i]; j < currentEnd; j++ {
			hourlyMeetingCountMap[j]++
		}

		// Meeting could be cross day
		if isMeetingCrossDay {
			for j := 0; j < end[i]; j++ {
				hourlyMeetingCountMap[j]++
			}
		}
	}

	return findMaxOverlap(hourlyMeetingCountMap)

}

func createMeetingCountMap() map[int]int {
	hourlyMeetingCountMap := make(map[int]int)

	for i := 0; i < 24; i++ {
		hourlyMeetingCountMap[i] = 0
	}

	return hourlyMeetingCountMap
}

func findMaxOverlap(hourlyMeetingCountMap map[int]int) int {
	maxOverlap := 0
	for _, count := range hourlyMeetingCountMap {
		if count > maxOverlap {
			maxOverlap = count
		}
	}

	return maxOverlap
}

/*

Given two arrays start[] and end[] such that start[i] is the starting time of ith meeting and end[i] is the ending time of ith meeting. Return the minimum number of rooms required to attend all meetings.

Note: A person can also attend a meeting if it's starting time is same as the previous meeting's ending time.

Examples:

Input: start[] = [1, 10, 7], end[] = [4, 15, 10]
Output: 1
Explanation: Since all the meetings are held at different times, it is possible to attend all the meetings in a single room.
Input: start[] = [2, 9, 6], end[] = [4, 12, 10]
Output: 2
Explanation: 1st and 2nd meetings at one room but for 3rd meeting one another room required.

*/
