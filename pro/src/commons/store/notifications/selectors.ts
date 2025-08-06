import { Notification } from '@/commons/store/notifications/reducer'
import { RootState } from '@/commons/store/rootReducer'

export const notificationSelector = (state: RootState): Notification | null => {
  return state.notification.notification
}

export const isStickyBarOpenSelector = (state: RootState): boolean => {
  return state.notification.isStickyBarOpen
}
