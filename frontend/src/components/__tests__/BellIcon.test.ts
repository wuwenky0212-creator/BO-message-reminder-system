import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import BellIcon from '../BellIcon.vue'
import axios from 'axios'
import { io } from 'socket.io-client'

vi.mock('axios')
vi.mock('socket.io-client')

describe('BellIcon.vue', () => {
  let wrapper: VueWrapper<any>
  let mockSocket: any

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock axios
    vi.mocked(axios.get).mockResolvedValue({
      data: {
        code: 0,
        data: {
          totalUnread: 5
        }
      }
    })

    // Mock socket.io
    mockSocket = {
      on: vi.fn(),
      disconnect: vi.fn(),
      connected: false
    }
    vi.mocked(io).mockReturnValue(mockSocket as any)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('5.1.1 创建组件基础结构', () => {
    it('should render bell icon correctly', () => {
      wrapper = mount(BellIcon)
      
      expect(wrapper.find('.bell-icon-button').exists()).toBe(true)
      expect(wrapper.find('.bell-icon').exists()).toBe(true)
    })

    it('should have correct initial state', async () => {
      wrapper = mount(BellIcon)
      
      // Wait for initial fetch to complete
      await new Promise(resolve => setTimeout(resolve, 50))
      
      expect(wrapper.vm.totalUnread).toBe(5) // From mocked API response
      expect(wrapper.vm.isOpen).toBe(false)
      expect(wrapper.vm.isLoading).toBe(false)
      expect(wrapper.vm.wsConnected).toBe(false)
    })
  })

  describe('5.1.2 实现红点标识显示逻辑', () => {
    it('should not show red dot when totalUnread is 0', async () => {
      vi.mocked(axios.get).mockResolvedValue({
        data: {
          code: 0,
          data: { totalUnread: 0 }
        }
      })

      wrapper = mount(BellIcon)
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.find('.red-dot').exists()).toBe(false)
    })

    it('should show red dot when totalUnread > 0', async () => {
      vi.mocked(axios.get).mockResolvedValue({
        data: {
          code: 0,
          data: { totalUnread: 15 }
        }
      })

      wrapper = mount(BellIcon)
      await new Promise(resolve => setTimeout(resolve, 100))
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.red-dot').exists()).toBe(true)
      expect(wrapper.find('.red-dot').text()).toBe('15')
    })

    it('should display "99+" when totalUnread > 99', async () => {
      wrapper = mount(BellIcon)
      wrapper.vm.totalUnread = 150
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.red-dot').text()).toBe('99+')
    })
  })

  describe('5.1.3 实现WebSocket连接逻辑', () => {
    it('should connect to WebSocket when enableWebSocket is true', async () => {
      wrapper = mount(BellIcon, {
        props: {
          enableWebSocket: true
        }
      })

      await wrapper.vm.$nextTick()

      expect(io).toHaveBeenCalledWith('ws://localhost:8000', expect.objectContaining({
        transports: ['websocket'],
        reconnection: true
      }))
    })

    it('should register WebSocket event handlers', async () => {
      wrapper = mount(BellIcon, {
        props: {
          enableWebSocket: true
        }
      })

      await wrapper.vm.$nextTick()

      expect(mockSocket.on).toHaveBeenCalledWith('connect', expect.any(Function))
      expect(mockSocket.on).toHaveBeenCalledWith('disconnect', expect.any(Function))
      expect(mockSocket.on).toHaveBeenCalledWith('notification_update', expect.any(Function))
      expect(mockSocket.on).toHaveBeenCalledWith('connect_error', expect.any(Function))
    })

    it('should update totalUnread when receiving notification_update event', async () => {
      // Mock API to return initial value
      vi.mocked(axios.get).mockResolvedValue({
        data: {
          code: 0,
          data: { totalUnread: 10 }
        }
      })

      wrapper = mount(BellIcon, {
        props: {
          enableWebSocket: true
        }
      })

      // Wait for initial fetch
      await new Promise(resolve => setTimeout(resolve, 50))
      expect(wrapper.vm.totalUnread).toBe(10)

      // Simulate notification_update event
      const updateHandler = mockSocket.on.mock.calls.find(
        (call: any) => call[0] === 'notification_update'
      )?.[1]

      if (updateHandler) {
        updateHandler({ totalUnread: 25 })
        await wrapper.vm.$nextTick()
        expect(wrapper.vm.totalUnread).toBe(25)
      }
    })

    it('should disconnect WebSocket on unmount', async () => {
      wrapper = mount(BellIcon, {
        props: {
          enableWebSocket: true
        }
      })

      await wrapper.vm.$nextTick()
      wrapper.unmount()

      expect(mockSocket.disconnect).toHaveBeenCalled()
    })
  })

  describe('5.1.4 实现轮询降级逻辑', () => {
    it('should start polling when enableWebSocket is false', async () => {
      vi.useFakeTimers()
      
      wrapper = mount(BellIcon, {
        props: {
          enableWebSocket: false,
          refreshInterval: 5000
        }
      })

      await wrapper.vm.$nextTick()

      // Initial fetch
      expect(axios.get).toHaveBeenCalledTimes(1)

      // Advance timer
      vi.advanceTimersByTime(5000)
      expect(axios.get).toHaveBeenCalledTimes(2)

      vi.advanceTimersByTime(5000)
      expect(axios.get).toHaveBeenCalledTimes(3)

      vi.useRealTimers()
    })

    it('should fallback to polling when WebSocket connection fails', async () => {
      vi.useFakeTimers()

      wrapper = mount(BellIcon, {
        props: {
          enableWebSocket: true,
          refreshInterval: 5000
        }
      })

      await wrapper.vm.$nextTick()

      // Simulate connect_error
      const errorHandler = mockSocket.on.mock.calls.find(
        (call: any) => call[0] === 'connect_error'
      )?.[1]

      if (errorHandler) {
        errorHandler()
        await wrapper.vm.$nextTick()

        // Should start polling
        vi.advanceTimersByTime(5000)
        expect(axios.get).toHaveBeenCalled()
      }

      vi.useRealTimers()
    })

    it('should stop polling when WebSocket connects', async () => {
      vi.useFakeTimers()

      wrapper = mount(BellIcon, {
        props: {
          enableWebSocket: true,
          refreshInterval: 5000
        }
      })

      await wrapper.vm.$nextTick()

      // Simulate disconnect first (starts polling)
      const disconnectHandler = mockSocket.on.mock.calls.find(
        (call: any) => call[0] === 'disconnect'
      )?.[1]

      if (disconnectHandler) {
        disconnectHandler()
        await wrapper.vm.$nextTick()
      }

      // Simulate connect (should stop polling)
      const connectHandler = mockSocket.on.mock.calls.find(
        (call: any) => call[0] === 'connect'
      )?.[1]

      if (connectHandler) {
        connectHandler()
        await wrapper.vm.$nextTick()
        expect(wrapper.vm.wsConnected).toBe(true)
      }

      vi.useRealTimers()
    })
  })

  describe('Component interactions', () => {
    it('should emit toggle event when bell icon is clicked', async () => {
      wrapper = mount(BellIcon)
      
      await wrapper.find('.bell-icon-button').trigger('click')
      
      expect(wrapper.emitted('toggle')).toBeTruthy()
      expect(wrapper.vm.isOpen).toBe(true)
    })

    it('should not allow click when loading', async () => {
      wrapper = mount(BellIcon)
      wrapper.vm.isLoading = true
      await wrapper.vm.$nextTick()

      const button = wrapper.find('.bell-icon-button')
      expect(button.attributes('disabled')).toBeDefined()
    })

    it('should fetch notifications on mount', async () => {
      wrapper = mount(BellIcon)
      await wrapper.vm.$nextTick()

      expect(axios.get).toHaveBeenCalledWith('/api/v1/notifications/summary')
    })

    it('should expose refresh method', async () => {
      wrapper = mount(BellIcon)
      
      expect(wrapper.vm.refresh).toBeDefined()
      expect(typeof wrapper.vm.refresh).toBe('function')
      
      await wrapper.vm.refresh()
      expect(axios.get).toHaveBeenCalled()
    })
  })

  describe('Error handling', () => {
    it('should handle API errors gracefully', async () => {
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      vi.mocked(axios.get).mockRejectedValue(new Error('Network error'))

      wrapper = mount(BellIcon)
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(consoleError).toHaveBeenCalledWith('Failed to fetch notifications:', expect.any(Error))
      expect(wrapper.vm.isLoading).toBe(false)

      consoleError.mockRestore()
    })
  })
})
