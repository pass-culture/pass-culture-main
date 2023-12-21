import { Notification } from 'store/notifications/reducer'
import { RootState } from 'store/reducers'

export const notificationSelector = (state: RootState): Notification | null => {
  return state.notification.notification
}

export const isStickyBarOpenSelector = (state: RootState): boolean => {
  return state.notification.isStickyBarOpen
}
