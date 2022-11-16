import { NotificationTypeEnum } from 'hooks/useNotification'

export const SET_IS_STICKYBAR_OPEN = 'SET_IS_STICKYBAR_OPEN'
export const CLOSE_NOTIFICATION = 'CLOSE_NOTIFICATION'
export const SHOW_NOTIFICATION = 'SHOW_NOTIFICATION'

export interface INotification {
  text: string | null
  type: NotificationTypeEnum
  duration?: number
}

interface IActionShowNotification {
  type: typeof SHOW_NOTIFICATION
  payload: INotification
}

export const showNotification = (
  payload: INotification
): IActionShowNotification => ({
  payload,
  type: SHOW_NOTIFICATION,
})

interface IActionCloseNotification {
  type: typeof CLOSE_NOTIFICATION
}

export const closeNotification = (): IActionCloseNotification => ({
  type: CLOSE_NOTIFICATION,
})

interface IActionSetIsStickyBarOpen {
  type: typeof SET_IS_STICKYBAR_OPEN
  payload: boolean
}

export const setIsStickyBarOpen = (
  payload: boolean
): IActionSetIsStickyBarOpen => ({
  payload,
  type: SET_IS_STICKYBAR_OPEN,
})

type TNotificationAction =
  | IActionCloseNotification
  | IActionShowNotification
  | IActionSetIsStickyBarOpen

interface INotificationState {
  isStickyBarOpen: boolean
  notification: INotification | null
}

export const notificationInitialState: INotificationState = {
  isStickyBarOpen: false,
  notification: null,
}

export const notificationReducer = (
  state = notificationInitialState,
  action: TNotificationAction
): INotificationState => {
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
