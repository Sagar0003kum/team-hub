<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useWorkspacesStore } from '@/stores/workspaces'
import { useProjectsStore } from '@/stores/projects'

const route = useRoute()
const workspacesStore = useWorkspacesStore()
const projectsStore = useProjectsStore()

const showCreateProjectModal = ref(false)
const newProject = ref({ name: '', description: '' })
const creating = ref(false)

onMounted(async () => {
  const workspaceId = parseInt(route.params.id)
  await workspacesStore.fetchWorkspace(workspaceId)
  await projectsStore.fetchProjects(workspaceId)
})

async function createProject() {
  if (!newProject.value.name.trim()) return

  creating.value = true
  try {
    await projectsStore.createProject({
      ...newProject.value,
      workspace_id: parseInt(route.params.id)
    })
    showCreateProjectModal.value = false
    newProject.value = { name: '', description: '' }
  } catch (error) {
    console.error('Failed to create project:', error)
  } finally {
    creating.value = false
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Loading State -->
    <div v-if="workspacesStore.loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>

    <template v-else-if="workspacesStore.currentWorkspace">
      <!-- Workspace Header -->
      <div class="mb-8">
        <div class="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <router-link to="/workspaces" class="hover:text-indigo-600">Workspaces</router-link>
          <span>/</span>
          <span class="text-gray-900">{{ workspacesStore.currentWorkspace.name }}</span>
        </div>
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">{{ workspacesStore.currentWorkspace.name }}</h1>
            <p class="text-gray-600 mt-1">{{ workspacesStore.currentWorkspace.description || 'No description' }}</p>
          </div>
          <button
            @click="showCreateProjectModal = true"
            class="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            New Project
          </button>
        </div>
      </div>

      <!-- Members Section -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Members</h3>
        <div class="flex flex-wrap gap-3">
          <div
            v-for="member in workspacesStore.currentWorkspace.members"
            :key="member.id"
            class="flex items-center space-x-2 bg-gray-50 rounded-lg px-3 py-2"
          >
            <div class="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
              <span class="text-indigo-600 font-medium text-sm">
                {{ member.user_display_name?.charAt(0)?.toUpperCase() || 'U' }}
              </span>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900">{{ member.user_display_name }}</p>
              <p class="text-xs text-gray-500 capitalize">{{ member.role }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Projects Section -->
      <div>
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Projects</h3>
        
        <div v-if="projectsStore.projects.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <router-link
            v-for="project in projectsStore.projects"
            :key="project.id"
            :to="`/projects/${project.id}`"
            class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:border-indigo-300 hover:shadow-md transition group"
          >
            <div class="flex items-start justify-between">
              <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center group-hover:bg-green-200 transition">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
              </div>
            </div>
            <h4 class="text-lg font-semibold text-gray-900 mt-4">{{ project.name }}</h4>
            <p class="text-gray-500 text-sm mt-1 line-clamp-2">{{ project.description || 'No description' }}</p>
            <div class="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
              <span class="text-xs text-gray-500">
                Created {{ new Date(project.created_at).toLocaleDateString() }}
              </span>
              <span class="text-indigo-600 text-sm font-medium group-hover:text-indigo-700">
                View →
              </span>
            </div>
          </router-link>
        </div>

        <!-- Empty State -->
        <div v-else class="bg-gray-50 rounded-xl border-2 border-dashed border-gray-300 p-12 text-center">
          <div class="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
          </div>
          <h3 class="text-gray-900 font-medium mb-1">No projects yet</h3>
          <p class="text-gray-500 text-sm mb-4">Create your first project to start managing tasks.</p>
          <button
            @click="showCreateProjectModal = true"
            class="text-indigo-600 hover:text-indigo-700 font-medium text-sm"
          >
            + Create Project
          </button>
        </div>
      </div>
    </template>

    <!-- Create Project Modal -->
    <div v-if="showCreateProjectModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Create Project</h2>
        
        <form @submit.prevent="createProject" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              v-model="newProject.name"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              placeholder="My Project"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              v-model="newProject.description"
              rows="3"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none resize-none"
              placeholder="What's this project about?"
            ></textarea>
          </div>

          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="showCreateProjectModal = false"
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
