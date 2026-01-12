<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import { useTasksStore } from '@/stores/tasks'

const route = useRoute()
const projectsStore = useProjectsStore()
const tasksStore = useTasksStore()

const showCreateTaskModal = ref(false)
const showTaskDetailModal = ref(false)
const selectedTask = ref(null)
const draggedTask = ref(null)

const newTask = ref({
  title: '',
  description: '',
  priority: 'medium',
  status: 'todo'
})
const creating = ref(false)

const columns = [
  { id: 'todo', title: 'To Do', color: 'gray' },
  { id: 'in_progress', title: 'In Progress', color: 'blue' },
  { id: 'review', title: 'Review', color: 'yellow' },
  { id: 'done', title: 'Done', color: 'green' }
]

const priorityColors = {
  low: 'bg-gray-100 text-gray-700',
  medium: 'bg-blue-100 text-blue-700',
  high: 'bg-orange-100 text-orange-700',
  urgent: 'bg-red-100 text-red-700'
}

onMounted(async () => {
  const projectId = parseInt(route.params.id)
  await projectsStore.fetchProject(projectId)
  await tasksStore.fetchTasks(projectId)
})

function getColumnTasks(status) {
  return tasksStore.tasksByStatus[status] || []
}

function onDragStart(task) {
  draggedTask.value = task
}

function onDragOver(event) {
  event.preventDefault()
}

async function onDrop(newStatus) {
  if (!draggedTask.value) return

  const task = draggedTask.value
  const newPosition = getColumnTasks(newStatus).length

  tasksStore.moveTask(task.id, newStatus, newPosition)

  try {
    await tasksStore.updateTaskPosition(task.id, newStatus, newPosition)
  } catch (error) {
    console.error('Failed to update task position:', error)
    await tasksStore.fetchTasks(parseInt(route.params.id))
  }

  draggedTask.value = null
}

async function createTask() {
  if (!newTask.value.title.trim()) return

  creating.value = true
  try {
    await tasksStore.createTask({
      ...newTask.value,
      project_id: parseInt(route.params.id)
    })
    showCreateTaskModal.value = false
    newTask.value = { title: '', description: '', priority: 'medium', status: 'todo' }
  } catch (error) {
    console.error('Failed to create task:', error)
  } finally {
    creating.value = false
  }
}

function openTaskDetail(task) {
  selectedTask.value = { ...task }
  showTaskDetailModal.value = true
}

async function updateTask() {
  try {
    await tasksStore.updateTask(selectedTask.value.id, {
      title: selectedTask.value.title,
      description: selectedTask.value.description,
      priority: selectedTask.value.priority,
      status: selectedTask.value.status
    })
    showTaskDetailModal.value = false
  } catch (error) {
    console.error('Failed to update task:', error)
  }
}

async function deleteTask() {
  if (!confirm('Are you sure you want to delete this task?')) return

  try {
    await tasksStore.deleteTask(selectedTask.value.id)
    showTaskDetailModal.value = false
  } catch (error) {
    console.error('Failed to delete task:', error)
  }
}
</script>

<template>
  <div class="h-[calc(100vh-4rem)] flex flex-col">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2 text-sm text-gray-500">
          <router-link to="/workspaces" class="hover:text-indigo-600">Workspaces</router-link>
          <span>/</span>
          <router-link 
            v-if="projectsStore.currentProject"
            :to="`/workspaces/${projectsStore.currentProject.workspace_id}`" 
            class="hover:text-indigo-600"
          >
            Workspace
          </router-link>
          <span>/</span>
          <router-link 
            :to="`/projects/${route.params.id}`"
            class="hover:text-indigo-600"
          >
            {{ projectsStore.currentProject?.name }}
          </router-link>
          <span>/</span>
          <span class="text-gray-900">Board</span>
        </div>
        <button
          @click="showCreateTaskModal = true"
          class="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Add Task
        </button>
      </div>
    </div>

    <!-- Kanban Board -->
    <div class="flex-1 overflow-x-auto p-6 bg-gray-50">
      <div class="flex space-x-6 h-full min-w-max">
        <div
          v-for="column in columns"
          :key="column.id"
          class="w-80 flex-shrink-0 flex flex-col bg-gray-100 rounded-xl"
          @dragover="onDragOver"
          @drop="onDrop(column.id)"
        >
          <!-- Column Header -->
          <div class="p-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <div 
                  class="w-3 h-3 rounded-full"
                  :class="{
                    'bg-gray-400': column.color === 'gray',
                    'bg-blue-500': column.color === 'blue',
                    'bg-yellow-500': column.color === 'yellow',
                    'bg-green-500': column.color === 'green'
                  }"
                ></div>
                <h3 class="font-semibold text-gray-900">{{ column.title }}</h3>
              </div>
              <span class="text-sm text-gray-500 bg-gray-200 px-2 py-0.5 rounded-full">
                {{ getColumnTasks(column.id).length }}
              </span>
            </div>
          </div>

          <!-- Tasks -->
          <div class="flex-1 overflow-y-auto p-4 space-y-3">
            <div
              v-for="task in getColumnTasks(column.id)"
              :key="task.id"
              draggable="true"
              @dragstart="onDragStart(task)"
              @click="openTaskDetail(task)"
              class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 cursor-pointer hover:shadow-md transition"
            >
              <h4 class="font-medium text-gray-900 mb-2">{{ task.title }}</h4>
              <p v-if="task.description" class="text-sm text-gray-500 mb-3 line-clamp-2">
                {{ task.description }}
              </p>
              <div class="flex items-center justify-between">
                <span 
                  class="text-xs font-medium px-2 py-1 rounded-full capitalize"
                  :class="priorityColors[task.priority]"
                >
                  {{ task.priority }}
                </span>
                <div v-if="task.assignee_name" class="flex items-center space-x-1">
                  <div class="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center">
                    <span class="text-indigo-600 text-xs font-medium">
                      {{ task.assignee_name.charAt(0).toUpperCase() }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div
              v-if="getColumnTasks(column.id).length === 0"
              class="text-center py-8 text-gray-400 text-sm"
            >
              No tasks
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Task Modal -->
    <div v-if="showCreateTaskModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Create Task</h2>
        
        <form @submit.prevent="createTask" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input
              v-model="newTask.title"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              placeholder="Task title"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              v-model="newTask.description"
              rows="3"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none resize-none"
              placeholder="Task description"
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <select
                v-model="newTask.priority"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                v-model="newTask.status"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              >
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="review">Review</option>
                <option value="done">Done</option>
              </select>
            </div>
          </div>

          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="showCreateTaskModal = false"
              class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="creating"
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
            >
              {{ creating ? 'Creating...' : 'Create' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Task Detail Modal -->
    <div v-if="showTaskDetailModal && selectedTask" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl max-w-lg w-full mx-4 p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold text-gray-900">Task Details</h2>
          <button
            @click="showTaskDetailModal = false"
            class="text-gray-400 hover:text-gray-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <form @submit.prevent="updateTask" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input
              v-model="selectedTask.title"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              v-model="selectedTask.description"
              rows="4"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none resize-none"
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <select
                v-model="selectedTask.priority"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                v-model="selectedTask.status"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              >
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="review">Review</option>
                <option value="done">Done</option>
              </select>
            </div>
          </div>

          <div class="flex justify-between pt-4">
            <button
              type="button"
              @click="deleteTask"
              class="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition"
            >
              Delete
            </button>
            <div class="flex space-x-3">
              <button
                type="button"
                @click="showTaskDetailModal = false"
                class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
              >
                Save Changes
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
