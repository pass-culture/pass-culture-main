import { RootState } from 'commons/store/rootReducer'

export const selectOffererNames = (state: RootState) =>
  state.offerer.offererNames

export const selectCurrentOffererId = (state: RootState) =>
  state.offerer.selectedOffererId
