import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useWorkspacesStore = defineStore('workspaces', () => {
  const workspaces = ref([])
  const currentWorkspace = ref(null)
  const loading = ref(false)

  async function fetchWorkspaces() {
    loading.value = true
    try {
      const response = await api.get('/workspaces/')
      workspaces.value = response.data
      return workspaces.value
    } finally {
      loading.value = false
    }
  }

  async function fetchWorkspace(id) {
    loading.value = true
    try {
      const response = await api.get(`/workspaces/${id}`)
      currentWorkspace.value = response.data
      return currentWorkspace.value
    } finally {
      loading.value = false
    }
  }

  async function createWorkspace(data) {
    const response = await api.post('/workspaces/', data)
    workspaces.value.push(response.data)
    return response.data
  }

  async function updateWorkspace(id, data) {
    const response = await api.patch(`/workspaces/${id}`, data)
    const index = workspaces.value.findIndex(w => w.id === id)
    if (index !== -1) {
      workspaces.value[index] = response.data
    }
    if (currentWorkspace.value?.id === id) {
      currentWorkspace.value = { ...currentWorkspace.value, ...response.data }
    }
    return response.data
  }

  async function deleteWorkspace(id) {
    await api.delete(`/workspaces/${id}`)
    workspaces.value = workspaces.value.filter(w => w.id !== id)
    if (currentWorkspace.value?.id === id) {
      currentWorkspace.value = null
    }
  }

  async function addMember(workspaceId, userId, role = 'member') {
    const response = await api.post(`/workspaces/${workspaceId}/members`, {
      user_id: userId,
      role
    })
    if (currentWorkspace.value?.id === workspaceId) {
      currentWorkspace.value.members.push(response.data)
    }
    return response.data
  }

  async function removeMember(workspaceId, userId) {
    await api.delete(`/workspaces/${workspaceId}/members/${userId}`)
    if (currentWorkspace.value?.id === workspaceId) {
      currentWorkspace.value.members = currentWorkspace.value.members.filter(
        m => m.user_id !== userId
      )
    }
  }

  return {
    workspaces,
    currentWorkspace,
    loading,
    fetchWorkspaces,
    fetchWorkspace,
    createWorkspace,
    updateWorkspace,
    deleteWorkspace,
    addMember,
    removeMember
  }
})
