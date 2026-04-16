<template>
  <div class="bell-icon-container">
    <button 
      class="bell-icon-button" 
      @click="togglePanel"
      :disabled="isLoading"
      aria-label="通知铃铛"
    >
      <Bell class="bell-icon-svg" style="width: 16px; height: 16px;" />
      <span v-if="totalUnread > 0" class="red-badge">{{ totalUnread > 99 ? '99+' : totalUnread }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { io, Socket } from 'socket.io-client'
import axios from 'axios'
import { Bell } from '@element-plus/icons-vue'

interface BellIconProps {
  refreshInterval?: number
  enableWebSocket?: boolean
}

const props = withDefaults(defineProps<BellIconProps>(), {
  refreshInterval: 30000,
  enableWebSocket: true
})

const emit = defineEmits<{
  toggle: []
  refresh: []
}>()

const totalUnread = ref(0)
const isOpen = ref(false)
const isLoading = ref(false)
const wsConnected = ref(false)

let socket: Socket | null = null
let pollingTimer: ReturnType<typeof setInterval> | null = null

const fetchNotifications = async () => {
  try {
    isLoading.value = true
    const response = await axios.get('/api/v1/notifications/summary')
    if (response.data.code === 0) {
      totalUnread.value = response.data.data.totalUnread
    }
  } catch (error) {
    console.error('Failed to fetch notifications:', error)
  } finally {
    isLoading.value = false
  }
}

const connectWebSocket = () => {
  if (!props.enableWebSocket) {
    startPolling()
    return
  }

  try {
    // Use environment variable for WebSocket URL
    const wsUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const wsProtocol = wsUrl.startsWith('https') ? 'wss' : 'ws'
    const wsHost = wsUrl.replace(/^https?:\/\//, '')
    
    socket = io(`${wsProtocol}://${wsHost}`, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    })

    socket.on('connect', () => {
      wsConnected.value = true
      console.log('WebSocket connected')
      stopPolling()
    })

    socket.on('disconnect', () => {
      wsConnected.value = false
      console.log('WebSocket disconnected, falling back to polling')
      startPolling()
    })

    socket.on('notification_update', (data: { totalUnread: number }) => {
      totalUnread.value = data.totalUnread
    })

    socket.on('connect_error', () => {
      console.error('WebSocket connection failed, using polling')
      wsConnected.value = false
      startPolling()
    })
  } catch (error) {
    console.error('WebSocket setup failed:', error)
    startPolling()
  }
}

const startPolling = () => {
  if (pollingTimer) return
  
  pollingTimer = setInterval(() => {
    fetchNotifications()
  }, props.refreshInterval)
}

const stopPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

const togglePanel = () => {
  isOpen.value = !isOpen.value
  emit('toggle')
}

const cleanup = () => {
  if (socket) {
    socket.disconnect()
    socket = null
  }
  stopPolling()
}

onMounted(() => {
  fetchNotifications()
  connectWebSocket()
})

onUnmounted(() => {
  cleanup()
})

defineExpose({
  totalUnread,
  isOpen,
  isLoading,
  wsConnected,
  refresh: fetchNotifications
})
</script>

<style scoped>
.bell-icon-container {
  position: relative;
  display: inline-block;
}

.bell-icon-button {
  position: relative;
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s;
  color: rgba(255, 255, 255, 0.85);
}

.bell-icon-button:hover {
  color: white;
  transform: scale(1.1);
}

.bell-icon-button:active {
  transform: scale(0.95);
}

.bell-icon-button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.bell-icon-svg {
  flex-shrink: 0;
}

.red-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: linear-gradient(135deg, #f5222d 0%, #ff4d4f 100%);
  color: white;
  border-radius: 10px;
  padding: 2px 5px;
  font-size: 10px;
  font-weight: 600;
  min-width: 16px;
  height: 16px;
  text-align: center;
  line-height: 12px;
  box-shadow: 0 2px 4px rgba(245, 34, 45, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.3);
}
</style>
