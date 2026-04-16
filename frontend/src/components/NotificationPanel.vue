<template>
  <div v-if="isVisible" class="notification-panel" @click.stop>
    <!-- 面板头部 -->
    <div class="panel-header">
      <div class="header-left">
        <Bell class="header-icon" style="width: 16px; height: 16px; color: #1890ff;" />
        <h3 class="header-title">提醒事项</h3>
        <button class="settings-btn" @click="handleSettings" aria-label="设置">
          <Setting style="width: 14px; height: 14px; color: #8c8c8c;" />
        </button>
      </div>
      <div class="header-right">
        <div class="segmented-control">
          <button 
            :class="['segment-btn', { active: activeTab === 'message' }]"
            @click="activeTab = 'message'"
          >
            消息处理
          </button>
          <button 
            :class="['segment-btn', { active: activeTab === 'exception' }]"
            @click="activeTab = 'exception'"
          >
            异常处理
          </button>
        </div>
      </div>
    </div>

    <!-- 面板内容区 -->
    <div class="panel-content">
      <div v-if="isLoading" class="loading">加载中...</div>
      
      <div v-else-if="currentNotifications.length === 0" class="empty">
        <div class="empty-text">暂时没有更多了</div>
      </div>
      
      <div v-else class="notification-list">
        <div 
          v-for="(item, index) in currentNotifications" 
          :key="index"
          class="notification-item"
          @click="handleItemClick(item)"
        >
          <div class="item-main">
            <WarningFilled class="warning-icon" style="width: 16px; height: 16px; color: #fa8c16;" />
            <span class="item-title">{{ item.title }}</span>
            <span class="item-count">({{ item.count }})</span>
            <a href="#" class="item-action" @click.stop="handleAction(item)">去处理 &gt;</a>
          </div>
          <div class="item-time">{{ item.lastUpdated }}</div>
        </div>
      </div>
    </div>

    <!-- 底部提示 -->
    <div v-if="!isLoading && currentNotifications.length > 0" class="panel-footer">
      <span class="footer-text">暂时没有更多了</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import apiClient from '../api/axios'
import { Bell, Setting, WarningFilled } from '@element-plus/icons-vue'

interface NotificationItem {
  ruleCode: string
  title: string
  count: number
  lastUpdated: string
  status: string
  priority: string
}

interface NotificationData {
  tabs: {
    message: NotificationItem[]
    exception: NotificationItem[]
  }
  totalUnread: number
  lastRefreshTime: string
}

interface Props {
  isVisible: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  action: [ruleCode: string]
}>()

const activeTab = ref<'message' | 'exception'>('exception')
const notifications = ref<NotificationData | null>(null)
const isLoading = ref(false)

const currentNotifications = computed(() => {
  if (!notifications.value) return []
  return activeTab.value === 'exception' 
    ? notifications.value.tabs.exception 
    : notifications.value.tabs.message
})

const fetchNotifications = async () => {
  try {
    isLoading.value = true
    const response = await apiClient.get('/api/v1/notifications/summary')
    if (response.data.code === 0) {
      notifications.value = response.data.data
    }
  } catch (error) {
    console.error('Failed to fetch notifications:', error)
  } finally {
    isLoading.value = false
  }
}

const handleSettings = () => {
  console.log('打开设置')
  // TODO: 跳转到设置页面或弹出设置弹窗
}

const handleItemClick = (item: NotificationItem) => {
  console.log('点击消息项:', item)
  emit('action', item.ruleCode)
  emit('close')
}

const handleAction = (item: NotificationItem) => {
  console.log('去处理:', item)
  emit('action', item.ruleCode)
  emit('close')
}

watch(() => props.isVisible, (visible) => {
  if (visible) {
    fetchNotifications()
  }
})
</script>

<style scoped>
.notification-panel {
  position: fixed;
  top: 56px;
  right: 80px;
  width: 380px;
  max-height: 520px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

/* 面板头部 */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid #f0f0f0;
  gap: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  flex-shrink: 0;
}

.header-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #262626;
  letter-spacing: 0.3px;
}

.settings-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  border-radius: 4px;
}

.settings-btn:hover {
  background: #f5f5f5;
}

.header-right {
  flex-shrink: 0;
}

/* 分段控制器 */
.segmented-control {
  display: flex;
  gap: 0;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  overflow: hidden;
}

.segment-btn {
  padding: 4px 12px;
  background: white;
  border: none;
  cursor: pointer;
  font-size: 13px;
  color: #595959;
  transition: all 0.2s;
  white-space: nowrap;
  font-weight: 450;
}

.segment-btn:not(:last-child) {
  border-right: 1px solid #d9d9d9;
}

.segment-btn:hover {
  background: #fafafa;
}

.segment-btn.active {
  background: white;
  color: #1890ff;
  border-color: #1890ff;
  font-weight: 600;
  position: relative;
  z-index: 1;
}

.segment-btn.active + .segment-btn {
  border-left-color: #1890ff;
}

/* 面板内容区 */
.panel-content {
  flex: 1;
  overflow-y: auto;
  max-height: 400px;
}

.loading, .empty {
  padding: 60px 20px;
  text-align: center;
  color: #bfbfbf;
  font-size: 13px;
}

.empty-text {
  color: #bfbfbf;
}

.notification-list {
  padding: 0;
}

/* 消息项 */
.notification-item {
  padding: 14px 16px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  transition: background 0.2s;
}

.notification-item:hover {
  background: #fafafa;
}

.notification-item:last-child {
  border-bottom: none;
}

.item-main {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.warning-icon {
  flex-shrink: 0;
}

.item-title {
  font-size: 14px;
  color: #262626;
  font-weight: 500;
}

.item-count {
  font-size: 14px;
  color: #595959;
  font-weight: 400;
}

.item-action {
  margin-left: auto;
  color: #1890ff;
  text-decoration: none;
  font-size: 13px;
  white-space: nowrap;
  font-weight: 500;
  transition: color 0.2s;
}

.item-action:hover {
  color: #40a9ff;
}

.item-time {
  font-size: 12px;
  color: #8c8c8c;
  padding-left: 24px;
}

/* 底部提示 */
.panel-footer {
  padding: 12px 16px;
  text-align: center;
  border-top: 1px solid #f5f5f5;
}

.footer-text {
  font-size: 12px;
  color: #bfbfbf;
}

/* 滚动条样式 */
.panel-content::-webkit-scrollbar {
  width: 6px;
}

.panel-content::-webkit-scrollbar-track {
  background: #f5f5f5;
}

.panel-content::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 3px;
}

.panel-content::-webkit-scrollbar-thumb:hover {
  background: #bfbfbf;
}
</style>
