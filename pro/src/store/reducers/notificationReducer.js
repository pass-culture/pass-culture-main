export const CLOSE_NOTIFICATION = 'CLOSE_NOTIFICATION'
export const SHOW_NOTIFICATION = 'SHOW_NOTIFICATION'

export const initialState = null

export const notificationReducer = (state = initialState, action) => {
  switch (action.type) {
    case CLOSE_NOTIFICATION:
      return initialState
    case SHOW_NOTIFICATION:
      return { ...action.payload }
    default:
      return state
  }
}

export const closeNotification = () => ({
  type: CLOSE_NOTIFICATION,
})

export const showNotification = payload => ({
  payload,
  type: SHOW_NOTIFICATION,
})
