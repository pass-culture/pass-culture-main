import type { RootState } from '@/commons/store/rootReducer'

export const selectVenueTypes = (state: RootState) =>
  state.venueTypes.venueTypes
