import { RootState } from 'store/reducers'
import { INotification } from 'store/reducers/notificationReducer'

export const notificationSelector = (
  state: RootState
): INotification | null => {
  return state.notification.notification
}
export const isStickyBarOpenSelector = (state: RootState): boolean => {
  return state.notification.isStickyBarOpen
}
