<script setup>
import { ref, onMounted } from 'vue'
import { useWorkspacesStore } from '@/stores/workspaces'

const workspacesStore = useWorkspacesStore()
const showCreateModal = ref(false)
const newWorkspace = ref({ name: '', description: '' })
const creating = ref(false)

onMounted(() => {
  workspacesStore.fetchWorkspaces()
})

async function createWorkspace() {
  if (!newWorkspace.value.name.trim()) return

  creating.value = true
  try {
    await workspacesStore.createWorkspace(newWorkspace.value)
    showCreateModal.value = false
    newWorkspace.value = { name: '', description: '' }
  } catch (error) {
    console.error('Failed to create workspace:', error)
  } finally {
    creating.value = false
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Workspaces</h1>
        <p class="text-gray-600 mt-1">Manage your team workspaces</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
      >
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        New Workspace
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="workspacesStore.loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>

    <!-- Workspaces Grid -->
    <div v-else-if="workspacesStore.workspaces.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <router-link
        v-for="workspace in workspacesStore.workspaces"
        :key="workspace.id"
        :to="`/workspaces/${workspace.id}`"
        class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:border-indigo-300 hover:shadow-md transition group"
      >
        <div class="flex items-start justify-between">
          <div class="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center group-hover:bg-indigo-200 transition">
            <span class="text-indigo-600 font-bold text-xl">{{ workspace.name.charAt(0).toUpperCase() }}</span>
          </div>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mt-4">{{ workspace.name }}</h3>
        <p class="text-gray-500 text-sm mt-1 line-clamp-2">{{ workspace.description || 'No description' }}</p>
        <div class="mt-4 pt-4 border-t border-gray-100">
          <span class="text-xs text-gray-500">
            Created {{ new Date(workspace.created_at).toLocaleDateString() }}
          </span>
        </div>
      </router-link>
    </div>

    <!-- Empty State -->
    <div v-else class="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
      <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No workspaces yet</h3>
      <p class="text-gray-500 mb-4">Create your first workspace to get started.</p>
      <button
        @click="showCreateModal = true"
        class="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
      >
        Create Workspace
      </button>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Create Workspace</h2>
        
        <form @submit.prevent="createWorkspace" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              v-model="newWorkspace.name"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              placeholder="My Workspace"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              v-model="newWorkspace.description"
              rows="3"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none resize-none"
              placeholder="What's this workspace for?"
            ></textarea>
          </div>

          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="showCreateModal = false"
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
  </div>
</template>
