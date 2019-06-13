import {createSelector} from "reselect";

export const selectNonVirtualVenues = createSelector(
  state => state.data.venues,
  venues => venues.filter(venue => venue.isVirtual === false)
)

export default selectNonVirtualVenues
