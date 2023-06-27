import { NotificationTypeEnum } from 'hooks/useNotification'

export const SET_IS_STICKYBAR_OPEN = 'SET_IS_STICKYBAR_OPEN'
export const CLOSE_NOTIFICATION = 'CLOSE_NOTIFICATION'
export const SHOW_NOTIFICATION = 'SHOW_NOTIFICATION'

export interface Notification {
  text: string | null
  type: NotificationTypeEnum
  duration?: number
}

interface ActionShowNotification {
  type: typeof SHOW_NOTIFICATION
  payload: Notification
}

export const showNotification = (
  payload: Notification
): ActionShowNotification => ({
  payload,
  type: SHOW_NOTIFICATION,
})

interface ActionCloseNotification {
  type: typeof CLOSE_NOTIFICATION
}

export const closeNotification = (): ActionCloseNotification => ({
  type: CLOSE_NOTIFICATION,
})

interface ActionSetIsStickyBarOpen {
  type: typeof SET_IS_STICKYBAR_OPEN
  payload: boolean
}

export const setIsStickyBarOpen = (
  payload: boolean
): ActionSetIsStickyBarOpen => ({
  payload,
  type: SET_IS_STICKYBAR_OPEN,
})

type NotificationAction =
  | ActionCloseNotification
  | ActionShowNotification
  | ActionSetIsStickyBarOpen

interface NotificationState {
  isStickyBarOpen: boolean
  notification: Notification | null
}

export const notificationInitialState: NotificationState = {
  isStickyBarOpen: false,
  notification: null,
}

export const notificationReducer = (
  state = notificationInitialState,
  action: NotificationAction
): NotificationState => {
  switch (action.type) {
    case CLOSE_NOTIFICATION:
      return { ...state, notification: null }
    case SHOW_NOTIFICATION:
      return { ...state, notification: action.payload }
    case SET_IS_STICKYBAR_OPEN:
      return { ...state, isStickyBarOpen: action.payload }
    default:
      return state
  }
}
