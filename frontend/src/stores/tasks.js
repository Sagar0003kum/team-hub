import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref([])
  const loading = ref(false)

  const tasksByStatus = computed(() => {
    return {
      todo: tasks.value.filter(t => t.status === 'todo'),
      in_progress: tasks.value.filter(t => t.status === 'in_progress'),
      review: tasks.value.filter(t => t.status === 'review'),
      done: tasks.value.filter(t => t.status === 'done')
    }
  })

  async function fetchTasks(projectId = null) {
    loading.value = true
    try {
      const params = projectId ? { project_id: projectId } : {}
      const response = await api.get('/tasks/', { params })
      tasks.value = response.data
      return tasks.value
    } finally {
      loading.value = false
    }
  }

  async function fetchTask(id) {
    const response = await api.get(`/tasks/${id}`)
    return response.data
  }

  async function createTask(data) {
    const response = await api.post('/tasks/', data)
    tasks.value.push(response.data)
    return response.data
  }

  async function updateTask(id, data) {
    const response = await api.patch(`/tasks/${id}`, data)
    const index = tasks.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tasks.value[index] = response.data
    }
    return response.data
  }

  async function updateTaskPosition(id, status, position) {
    const response = await api.patch(`/tasks/${id}/position`, { status, position })
    const index = tasks.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tasks.value[index] = response.data
    }
    return response.data
  }

  async function deleteTask(id) {
    await api.delete(`/tasks/${id}`)
    tasks.value = tasks.value.filter(t => t.id !== id)
  }

  function moveTask(taskId, newStatus, newPosition) {
    const task = tasks.value.find(t => t.id === taskId)
    if (task) {
      task.status = newStatus
      task.position = newPosition
    }
  }

  return {
    tasks,
    loading,
    tasksByStatus,
    fetchTasks,
    fetchTask,
    createTask,
    updateTask,
    updateTaskPosition,
    deleteTask,
    moveTask
  }
})
