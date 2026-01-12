import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref([])
  const currentProject = ref(null)
  const loading = ref(false)

  async function fetchProjects(workspaceId = null) {
    loading.value = true
    try {
      const params = workspaceId ? { workspace_id: workspaceId } : {}
      const response = await api.get('/projects/', { params })
      projects.value = response.data
      return projects.value
    } finally {
      loading.value = false
    }
  }

  async function fetchProject(id) {
    loading.value = true
    try {
      const response = await api.get(`/projects/${id}`)
      currentProject.value = response.data
      return currentProject.value
    } finally {
      loading.value = false
    }
  }

  async function createProject(data) {
    const response = await api.post('/projects/', data)
    projects.value.push(response.data)
    return response.data
  }

  async function updateProject(id, data) {
    const response = await api.patch(`/projects/${id}`, data)
    const index = projects.value.findIndex(p => p.id === id)
    if (index !== -1) {
      projects.value[index] = response.data
    }
    if (currentProject.value?.id === id) {
      currentProject.value = response.data
    }
    return response.data
  }

  async function deleteProject(id) {
    await api.delete(`/projects/${id}`)
    projects.value = projects.value.filter(p => p.id !== id)
    if (currentProject.value?.id === id) {
      currentProject.value = null
    }
  }

  return {
    projects,
    currentProject,
    loading,
    fetchProjects,
    fetchProject,
    createProject,
    updateProject,
    deleteProject
  }
})
