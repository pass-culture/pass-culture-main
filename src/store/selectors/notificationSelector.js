export const notificationV1Selector = state => {
  if (state.notification && state.notification.version === 1) {
    return state.notification
  } else {
    return null
  }
}
export const notificationV2Selector = state => {
  if (state.notification && state.notification.version === 2) {
    return state.notification
  } else {
    return {}
  }
}
