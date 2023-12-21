import { RootState } from 'store/rootReducer'

export const selectCurrentUser = (state: RootState) => state.user.currentUser
