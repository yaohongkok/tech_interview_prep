# LeetCode 207 - Course Schedule
#
# Key Tricks:
#  - Create dependency graph
#  - Create reverse dependecy graph
#  - Use BFS to visit all possible courses
#  - If all courses taken == numCourses, then it is possible to take all courses


from collections import deque

class Solution:
    def createDependencyGraph(self, prerequisites, numCourses) -> dict[int, list[int]]:
        dependency_g = {c: [] for c in range(numCourses)}

        for pr in prerequisites:
            cur = pr[0]
            prereq = pr[1]

            dependency_g[cur].append(prereq)
        
        return dependency_g

    def createReverseDepGraph(self, prerequisites, numCourses) -> dict[int, list[int]]:
        rev_dep_g = {}

        for pr in prerequisites:
            cur = pr[0]
            prereq = pr[1]

            rev_dep_g.setdefault(prereq, []).append(cur)
        
        return rev_dep_g

    def updateGraphsAndQueue(self, dg, rdg, q, courseTook, course):
        dependentCourses = rdg.get(course, [])

        for dc in dependentCourses:
            dg[dc].remove(course)

            if len(dg[dc]) == 0 and dc not in courseTook:
                q.append(dc)
        

    def canFinish(self, numCourses: int, prerequisites: list[list[int]]) -> bool:
        if len(prerequisites) == 0:
            return True

        dg = self.createDependencyGraph(prerequisites, numCourses)
        rdg = self.createReverseDepGraph(prerequisites, numCourses)

        courses_no_prereq = [course for course, prereqs in dg.items() if len(prereqs) == 0]

        courseTook = set()

        q = deque(courses_no_prereq)

        while q:
            course = q.popleft()
            courseTook.add(course)

            if len(courseTook) == numCourses:
                return True

            self.updateGraphsAndQueue(dg, rdg, q, courseTook, course)

        return False
        