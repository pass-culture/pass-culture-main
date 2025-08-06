import { RootState } from '@/commons/store/rootReducer'

export const selectOffererNames = (state: RootState) =>
  state.offerer.offererNames

export const selectCurrentOfferer = (state: RootState) =>
  state.offerer.currentOfferer

export const selectCurrentOffererId = (state: RootState) =>
  state.offerer.currentOfferer?.id ?? null

export const selectCurrentOffererIsOnboarded = (state: RootState) =>
  state.offerer.currentOfferer?.isOnboarded ?? null
