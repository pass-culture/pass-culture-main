import type { Notification } from '@/commons/store/notifications/reducer'
import type { RootState } from '@/commons/store/store'

export const notificationSelector = (state: RootState): Notification | null => {
  return state.notification.notification
}

export const isStickyBarOpenSelector = (state: RootState): boolean => {
  return state.notification.isStickyBarOpen
}
