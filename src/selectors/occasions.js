import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.occasions,
  state => state.data.searchedOccasions,
  (state, ownProps) => ownProps.match.params.venueId,
  (occasions, searchedOccasions, venueId) => {
    if (!occasions && !searchedOccasions) return

    // RETURN FIRST OCCASIONS FROM SEARCH INPUT
    // IF WE HAVE SOME OF THEM
    if (searchedOccasions) return searchedOccasions

    // youngest are at the top of the list
    return occasions
      .filter(o => venueId ? o.occurences.some(occ =>occ.venueId === venueId) : true)
      .sort((o1, o2) => o2.dehumanizedId - o1.dehumanizedId)
  }
)
