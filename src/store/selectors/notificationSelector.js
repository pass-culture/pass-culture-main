export const notificationV1Selector = state => {
  return state.notification && state.notification.version === 1 ? state.notification : null
}
export const notificationV2Selector = state => {
  return state.notification && state.notification.version === 2 ? state.notification : {}
}
