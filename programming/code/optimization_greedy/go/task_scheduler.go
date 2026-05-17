type TaskManager struct {
    TaskCooldownMap map[byte]int
    TaskCountMap map[byte]int
    Cooldown int
}

func NewTaskManager(tasks []byte, cooldown int) *TaskManager {
    tm := &TaskManager{
        TaskCooldownMap: make(map[byte]int),
        TaskCountMap: make(map[byte]int),
        Cooldown: cooldown,
    }

    for _, task := range(tasks) {
        if _, ok := tm.TaskCooldownMap[task]; !ok {
            tm.TaskCooldownMap[task] = 0
        }

        if _, ok := tm.TaskCountMap[task]; !ok {
            tm.TaskCountMap[task] = 1
        } else {
            tm.TaskCountMap[task]++
        }
    }

    return tm
}

func (tm *TaskManager) GetRunnableTask() (byte, bool) {
    var runnableTasks []byte

    for key, cooldownVal := range tm.TaskCooldownMap {
        if cooldownVal == 0 {
            runnableTasks = append(runnableTasks, key)
        }
    }

    maxCount := 0
    var maxCountTask byte = '0'

    if len(runnableTasks) == 0 {
        return '-', false
    } else {
        for _, task := range runnableTasks {
            if tm.TaskCountMap[task] > maxCount {
                maxCountTask = task
                maxCount = tm.TaskCountMap[task]
            }
        }
    }

    return maxCountTask, true
    
}

func (tm *TaskManager) RunTask(task byte) {
    cooldown := tm.TaskCooldownMap[task]

    if cooldown > 0 {
        panic("Running a task with >0 cooldown is not expected.")
    }

    if(tm.TaskCountMap[task] > 0) {
        tm.TaskCountMap[task]--
        tm.TaskCooldownMap[task] = tm.Cooldown + 1

        if (tm.TaskCountMap[task] == 0) {
            delete(tm.TaskCountMap, task)
            delete(tm.TaskCooldownMap, task)
        }
    } else {
        panic("A task is less than 0!")
    }
}

func (tm *TaskManager) DecreaseCooldown() {
    for key, cooldownVal := range tm.TaskCooldownMap {
        if cooldownVal > 0 {
            tm.TaskCooldownMap[key]--
        }
    }
}


func leastInterval(tasks []byte, n int) int {
    if len(tasks) == 0 {
        return 0
    }

    var tasksScheduled []byte = make([]byte, 0)
    tm := NewTaskManager(tasks, n)

    for len(tm.TaskCountMap) > 0 {
        runnableTask, canRun := tm.GetRunnableTask()
        
        if canRun {
            tasksScheduled = append(tasksScheduled, runnableTask)
            tm.RunTask(runnableTask)
        } else {
            tasksScheduled = append(tasksScheduled, '0')
        }

        tm.DecreaseCooldown()
    }

    // fmt.Println(string(tasksScheduled))

    return len(tasksScheduled)
}

