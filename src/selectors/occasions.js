import { createSelector } from 'reselect'

const emptyOccasions = []

export default createSelector(
  state => state.data.occasions,
  occasions => {
    if (!occasions) {
      return emptyOccasions
    }
    const sortedOccasions = [...occasions]
    // youngest are at the top of the list
    sortedOccasions.sort((o1, o2) => o2.dehumanizedId - o1.dehumanizedId)
    return sortedOccasions
  }
)
