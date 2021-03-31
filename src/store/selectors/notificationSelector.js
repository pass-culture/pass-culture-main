export const notificationV2Selector = state => {
  return state.notification && state.notification.version === 2 ? state.notification : {}
}
