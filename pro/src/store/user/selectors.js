export const selectUserInitialized = state => state.user.initialized

export const selectCurrentUser = state => state.user.currentUser

export const selectIsUserAdmin = state => state.user.currentUser?.isAdmin
