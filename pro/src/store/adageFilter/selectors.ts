import { RootState } from 'store/rootReducer'

export const adageFilterSelector = (state: RootState) =>
  state.adageFilter.adageFilter

export const adageQuerySelector = (state: RootState) =>
  state.adageFilter.adageQuery

export const adageSearchViewSelector = (state: RootState) =>
  state.adageFilter.searchView

export const adagePageSavedSelector = (state: RootState) =>
  state.adageFilter.adagePageSaved
