export const SET_NOTIFICATION = 'SET_NOTIFICATION'

// REDUCER
function notification(state, action) {
  switch (action.type) {
    case SET_NOTIFICATION:
      return action.notification
    default:
      return state
  }
}

// ACTION CREATORS
export function setNotification(notification) {
  console.log(' action setNotification ', notification);
  return {
    type: SET_NOTIFICATION,
    notification,
  }
}

// default
export default notification
