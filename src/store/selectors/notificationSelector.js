export const notificationV1Selector = state => {
  if (state.notification) {
    return state.notification.version === 1 ? state.notification : null
  } else {
    return null
  }
}
export const notificationV2Selector = state => {
  if (state.notification) {
    return state.notification.version === 2 ? state.notification : null
  } else {
    return null
  }
}
