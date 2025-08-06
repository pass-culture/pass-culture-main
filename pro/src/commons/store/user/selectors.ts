import { RootState } from '@/commons/store/rootReducer'

export const selectCurrentUser = (state: RootState) => state.user.currentUser
