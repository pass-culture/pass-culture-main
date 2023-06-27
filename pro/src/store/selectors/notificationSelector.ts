import { RootState } from 'store/reducers'
import { Notification } from 'store/reducers/notificationReducer'

export const notificationSelector = (state: RootState): Notification | null => {
  return state.notification.notification
}
export const isStickyBarOpenSelector = (state: RootState): boolean => {
  return state.notification.isStickyBarOpen
}
