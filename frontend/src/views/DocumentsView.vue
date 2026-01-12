<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import api from '@/services/api'

const route = useRoute()
const projectsStore = useProjectsStore()

const documents = ref([])
const loading = ref(true)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const selectedDocument = ref(null)

const newDocument = ref({ title: '', content: '' })
const creating = ref(false)
const saving = ref(false)

onMounted(async () => {
  const projectId = parseInt(route.params.id)
  await projectsStore.fetchProject(projectId)
  await fetchDocuments()
})

async function fetchDocuments() {
  loading.value = true
  try {
    const response = await api.get('/documents/', {
      params: { project_id: route.params.id }
    })
    documents.value = response.data
  } catch (error) {
    console.error('Failed to fetch documents:', error)
  } finally {
    loading.value = false
  }
}

async function createDocument() {
  if (!newDocument.value.title.trim()) return

  creating.value = true
  try {
    await api.post('/documents/', {
      ...newDocument.value,
      project_id: parseInt(route.params.id)
    })
    showCreateModal.value = false
    newDocument.value = { title: '', content: '' }
    await fetchDocuments()
  } catch (error) {
    console.error('Failed to create document:', error)
  } finally {
    creating.value = false
  }
}

function openDocument(doc) {
  selectedDocument.value = { ...doc }
  showEditModal.value = true
}

async function saveDocument() {
  saving.value = true
  try {
    await api.patch(`/documents/${selectedDocument.value.id}`, {
      title: selectedDocument.value.title,
      content: selectedDocument.value.content
    })
    showEditModal.value = false
    await fetchDocuments()
  } catch (error) {
    console.error('Failed to save document:', error)
  } finally {
    saving.value = false
  }
}

async function deleteDocument() {
  if (!confirm('Are you sure you want to delete this document?')) return

  try {
    await api.delete(`/documents/${selectedDocument.value.id}`)
    showEditModal.value = false
    await fetchDocuments()
  } catch (error) {
    console.error('Failed to delete document:', error)
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center space-x-2 text-sm text-gray-500 mb-2">
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
        <span class="text-gray-900">Documents</span>
      </div>
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Documents</h1>
          <p class="text-gray-600 mt-1">Create and manage project documents</p>
        </div>
        <button
          @click="showCreateModal = true"
          class="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          New Document
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>

    <!-- Documents Grid -->
    <div v-else-if="documents.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="doc in documents"
        :key="doc.id"
        @click="openDocument(doc)"
        class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 cursor-pointer hover:border-indigo-300 hover:shadow-md transition"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        </div>
        <h3 class="font-semibold text-gray-900 mb-2">{{ doc.title }}</h3>
        <p class="text-gray-500 text-sm line-clamp-2 mb-4">
          {{ doc.content || 'No content' }}
        </p>
        <div class="flex items-center justify-between text-xs text-gray-500">
          <span>By {{ doc.creator_name }}</span>
          <span>{{ new Date(doc.created_at).toLocaleDateString() }}</span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
      <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No documents yet</h3>
      <p class="text-gray-500 mb-4">Create your first document to get started.</p>
      <button
        @click="showCreateModal = true"
        class="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
      >
        Create Document
      </button>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Create Document</h2>
        
        <form @submit.prevent="createDocument" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input
              v-model="newDocument.title"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              placeholder="Document title"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Content</label>
            <textarea
              v-model="newDocument.content"
              rows="10"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none resize-none font-mono text-sm"
              placeholder="Start writing..."
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

    <!-- Edit Modal -->
    <div v-if="showEditModal && selectedDocument" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl max-w-4xl w-full mx-4 p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <input
            v-model="selectedDocument.title"
            type="text"
            class="text-xl font-semibold text-gray-900 border-none focus:outline-none focus:ring-0 p-0 w-full"
            placeholder="Document title"
          />
          <button
            @click="showEditModal = false"
            class="text-gray-400 hover:text-gray-600 ml-4"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <textarea
          v-model="selectedDocument.content"
          rows="20"
          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none resize-none font-mono text-sm"
          placeholder="Start writing..."
        ></textarea>

        <div class="flex justify-between pt-4">
          <button
            @click="deleteDocument"
            class="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition"
          >
            Delete
          </button>
          <div class="flex space-x-3">
            <button
              @click="showEditModal = false"
              class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
            >
              Cancel
            </button>
            <button
              @click="saveDocument"
              :disabled="saving"
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
            >
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
