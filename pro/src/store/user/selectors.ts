import { RootState } from 'store/reducers'

export const selectCurrentUser = (state: RootState) => state.user.currentUser
