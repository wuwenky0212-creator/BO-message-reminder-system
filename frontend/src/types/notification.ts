export interface NotificationItem {
  ruleCode: string
  title: string
  count: number
  lastUpdated: string
  status: 'success' | 'timeout' | 'error'
  priority: 'normal' | 'high' | 'critical'
}

export interface NotificationSummary {
  tabs: {
    message: NotificationItem[]
    exception: NotificationItem[]
  }
  totalUnread: number
  lastRefreshTime: string
}

export interface NotificationResponse {
  code: number
  message: string
  data: NotificationSummary
}
