export const CLOSE_NOTIFICATION = 'CLOSE_NOTIFICATION'
// DEPRECATED
export const SHOW_NOTIFICATION_V2 = 'SHOW_NOTIFICATION_V2'

export const initialState = {}

export const notificationReducer = (state = initialState, action) => {
  switch (action.type) {
    case CLOSE_NOTIFICATION:
      return initialState
    case SHOW_NOTIFICATION_V2:
      return { version: 2, ...action.payload }
    default:
      return state
  }
}

export const closeNotification = () => ({
  type: CLOSE_NOTIFICATION,
})

export const showNotificationV2 = payload => ({
  payload,
  type: SHOW_NOTIFICATION_V2,
})
