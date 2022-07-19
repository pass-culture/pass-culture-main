import { RootState } from 'store/reducers'

export const selectUserInitialized = (state: RootState) =>
  state.user.initialized

export const selectCurrentUser = (state: RootState) => state.user.currentUser

export const selectIsUserAdmin = (state: RootState) =>
  state.user.currentUser?.isAdmin
