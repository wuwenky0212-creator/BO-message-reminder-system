<template>
  <transition name="slide-fade">
    <div v-if="isVisible" class="risk-warning-modal">
      <!-- 红色标题栏 -->
      <div class="modal-header">
        <div class="header-left">
          <div class="warning-icon">
            <svg viewBox="0 0 24 24" width="32" height="32">
              <path fill="white" d="M12 2L1 21h22L12 2zm0 3.5L19.5 19h-15L12 5.5zM11 10v4h2v-4h-2zm0 6v2h2v-2h-2z"/>
            </svg>
          </div>
          <div class="header-text">
            <div class="title">风险预警：持仓卖空缺口</div>
            <div class="subtitle">{{ bondCode }} | {{ timestamp }}</div>
          </div>
        </div>
        <button class="close-btn" @click="close">✕</button>
      </div>

      <!-- 白色内容区 -->
      <div class="modal-body">
        <p class="warning-message">
          检测到可用数量小于0的债券标的，请立即补仓。
        </p>

        <!-- 统计卡片 -->
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-label">异常标的数</div>
            <div class="stat-value">{{ abnormalCount }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">风险敞口市值 (CNY)</div>
            <div class="stat-value risk-amount">{{ riskAmount }}</div>
          </div>
        </div>

        <!-- 债券列表 -->
        <div class="bond-list">
          <div class="list-header">
            <span class="col-code">证券代码</span>
            <span class="col-name">证券简称</span>
            <span class="col-gap">可用缺口</span>
          </div>
          <div v-for="(bond, index) in bonds" :key="index" class="list-row">
            <span class="col-code">{{ bond.code }}</span>
            <span class="col-name">{{ bond.name }}</span>
            <span class="col-gap risk-text">{{ bond.gap }}</span>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="modal-footer">
          <button class="action-btn" @click="handleAction">
            立即处理
            <svg class="arrow-icon" viewBox="0 0 24 24" width="16" height="16">
              <path fill="white" d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  isVisible: boolean
  bondCode?: string
  timestamp?: string
  abnormalCount?: number
  riskAmount?: string
  bonds?: Array<{ code: string; name: string; gap: string }>
}>()

const emit = defineEmits<{
  close: []
  action: []
}>()

const close = () => {
  emit('close')
}

const handleAction = () => {
  emit('action')
}
</script>

<style scoped>
.risk-warning-modal {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 420px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2), 0 4px 16px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  z-index: 2000;
  animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideIn {
  from {
    transform: translateX(120%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.slide-fade-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-enter-from {
  transform: translateX(120%);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(120%);
  opacity: 0;
}

/* 红色标题栏 */
.modal-header {
  background: linear-gradient(135deg, #f5222d 0%, #ff4d4f 100%);
  padding: 14px 18px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-left {
  display: flex;
  gap: 10px;
  align-items: center;
}

.warning-icon {
  width: 42px;
  height: 42px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-text {
  color: white;
}

.title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 3px;
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 12px;
  opacity: 0.9;
  font-weight: 400;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

/* 白色内容区 */
.modal-body {
  padding: 16px;
  background: white;
}

.warning-message {
  color: #595959;
  font-size: 13px;
  line-height: 1.6;
  margin: 0 0 14px 0;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 14px;
}

.stat-card {
  background: #fef0f0;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #ffccc7;
}

.stat-label {
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 26px;
  font-weight: 600;
  color: #f5222d;
  line-height: 1;
}

.risk-amount {
  font-size: 24px;
}

/* 债券列表 */
.bond-list {
  background: #fafafa;
  border-radius: 6px;
  padding: 10px;
  margin-bottom: 14px;
  border: 1px solid #f0f0f0;
}

.list-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  padding: 6px 10px;
  font-size: 12px;
  color: #8c8c8c;
  font-weight: 600;
  border-bottom: 1px solid #e8e8e8;
  margin-bottom: 6px;
}

.list-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  padding: 8px 10px;
  font-size: 13px;
  color: #262626;
  background: white;
  border-radius: 4px;
  margin-bottom: 4px;
}

.list-row:last-child {
  margin-bottom: 0;
}

.col-code {
  color: #595959;
}

.col-name {
  color: #262626;
}

.col-gap {
  text-align: right;
}

.risk-text {
  color: #f5222d;
  font-weight: 600;
}

/* 操作按钮 */
.modal-footer {
  display: flex;
  justify-content: flex-end;
}

.action-btn {
  background: linear-gradient(135deg, #f5222d 0%, #ff4d4f 100%);
  color: white;
  border: none;
  padding: 9px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(245, 34, 45, 0.3);
}

.action-btn:hover {
  background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
  box-shadow: 0 4px 16px rgba(245, 34, 45, 0.4);
  transform: translateY(-1px);
}

.action-btn:active {
  transform: translateY(0);
}

.arrow-icon {
  flex-shrink: 0;
}
</style>
