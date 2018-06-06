import { createSelector } from 'reselect'

const emptyOccasions = []

export default createSelector(
  state => state.data.occasions,
  state => state.data.searchedOccasions,
  (occasions, searchedOccasions) => {
    // RETURN FIRST OCCASIONS FROM SEARCH INPUT
    // IF WE HAVE SOME OF THEM
    if (searchedOccasions) {
      return searchedOccasions
    }
    if (!occasions) {
      return emptyOccasions
    }
    const sortedOccasions = [...occasions]
    // youngest are at the top of the list
    sortedOccasions.sort((o1, o2) => o2.dehumanizedId - o1.dehumanizedId)
    return sortedOccasions
  }
)
