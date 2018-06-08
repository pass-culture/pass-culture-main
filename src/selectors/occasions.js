import { createSelector } from 'reselect'

const emptyOccasions = []

export default createSelector(
  state => state.data.occasions,
  state => state.data.searchedOccasions,
  (state, ownProps) => ownProps.match.params.venueId,
  (occasions, searchedOccasions, venueId) => {
    // RETURN FIRST OCCASIONS FROM SEARCH INPUT
    // IF WE HAVE SOME OF THEM
    if (searchedOccasions) {
      return searchedOccasions
    }
    if (!occasions) {
      return emptyOccasions
    }

    let sortedOccasions
    // filter given maybe offerer and venue
    if (venueId) {
      sortedOccasions = occasions.filter(o => o.occurences.some(occ =>
        occ.venueId === venueId))
    } else {
      sortedOccasions = [...occasions]
    }

    // youngest are at the top of the list
    sortedOccasions.sort((o1, o2) => o2.dehumanizedId - o1.dehumanizedId)

    // return
    return sortedOccasions
  }
)
