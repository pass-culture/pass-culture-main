import { RootState } from 'store/rootReducer'

export const adageFilterSelector = (state: RootState) =>
  state.adageFilter.adageFilter

export const adageQuerySelector = (state: RootState) =>
  state.adageFilter.adageQuery
